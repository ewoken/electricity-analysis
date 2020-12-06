const fs = require('fs');
const mkdirp = require('mkdirp')

const fetch = require('isomorphic-fetch');
const { parse: parseHTML } = require('node-html-parser'); 
const FormData = require('form-data');
const { groupBy } = require('ramda');
Coordinates = require('coordinate-parser');

const { chunkAndChainPromises } = require('./helpers');

const WIND_POWER_NET_BASE_URL = 'https://www.thewindpower.net/'

async function getCountries() {
  const res = await fetch(`${WIND_POWER_NET_BASE_URL}/windfarms_list_en.php`);
  const html = await res.text();
  const doc = parseHTML(html);

  const countryOptions = doc.querySelectorAll('#id_form option')
  return countryOptions.map(c => ({
    id: c.getAttribute('value'),
    name: c.getAttribute('label'),
  })).filter(c => c.id != '-1')
}

async function getWindFarmList(countryId) {
  const form = new FormData();
  form.append('action', 'submit');
  form.append('pays', countryId);

  const res = await fetch(`${WIND_POWER_NET_BASE_URL}/windfarms_list_en.php`, {
    method: 'POST',
    body: form,
  });
  const html = await res.text();
  const doc = parseHTML(html);

  const windFarmLinks = doc.querySelectorAll('table a.lien_standard_tab');

  return Object.values(
    windFarmLinks.reduce((map, windFarmLink) => {
      const name = windFarmLink.innerHTML;
      const url = windFarmLink.getAttribute('href')
      const windFarm = map[name] || { name, url, partCount: 0 };
      windFarm.partCount += 1;
      return {
        ...map,
        [name]: windFarm,
      }
    }, {})
  )
}

function findUrls(v) {
  const regexp = /"([^"]+php)+"/g;
  let match = regexp.exec(v);
  const res = [];
  while (match) {
    res.push(match[1]);
    match = regexp.exec(v);
  }
  return res;
}

const STATUS = ["Operational", "Approved", "Under construction", "Planned"]
const converters = {
  'City': v => ({ city: v }),
  'Part': v => ({ name: v }),
  'Commissioning': v => ({ commissioningDate: v.replace('/', '-') + '-01' }),
  'Hub height': v => ({ hubHeight_m: Number(v.split(' ')[0]) }),
  'Total nominal power': v => ({ totalPower_kW: Number(v.split(' ')[0].replace(',', '')) }),
  "Developer": v => ({ developerUrls: findUrls(v) }),
  "Developers": v => ({ developerUrls: findUrls(v) }),
  "Operator": v => ({ operatorUrls: findUrls(v) }),
  "Operators": v => ({ operatorUrls: findUrls(v) }),
  "Owner": v => ({ ownerUrls: findUrls(v) }),
  "Owners": v => ({ ownerUrls: findUrls(v) }),
  "Source": () => {},
  "Turbine(s)": () => {},
  "Geodetic system": v => {
    if (v !== "WGS84") {
      console.log('Unknown geodetic system', v)
    }
  },
  "Precise location": v => ({ isLocationPrecise:  v === "yes" }),
  "Precise localization": v => ({ isLocationPrecise:  v === "yes" }),
  "Altitude": () => {},
  "Depth": v => ({ depth_m: Number(v.split(' ')[0]) }),
  "Distance from shore": v => ({ distanceToShore_km: Number(v.split(' ')[0]) }),
  "others": v => {
    let status = v.find(i => STATUS.includes(i) || i.includes("Dismantled"));
    let dismantlementDate = null;

    if (status && status.includes('Dismantled')) {
      const a = status.split(' ')
      status = a[0];
      dismantlementDate = a[1] ? Number(a[1].substr(1, 4)) : null;
    }

    return {
      dismantlementDate,
      status: status ? status.toUpperCase().replace(' ', '_') : "UNKNOWN",
      type: v.find(i => i.includes("Onshore")) ? "ONSHORE" : v.find(i => i.includes("Offshore")) ? "OFFSHORE" : "UNKNOWN",
    }
  }
}

function convertPart(part) {
  let coordinates = null
  if (part.Longitude && part.Latitude) {
    try {
      p = new Coordinates(part.Latitude + " " + part.Longitude)
      coordinates = [p.getLatitude(), p.getLongitude()]
    } catch {}
  }

  return Object.keys(part).reduce((obj, key) => {
    let newKey;
    if (key === "Latitude" || key === "Longitude") {
      return obj;
    } else if (key.includes('turbine')) {
      const urls = findUrls(part[key])
      newKey = {
        turbineCount: Number(key.split(' ')[0]),
        turbineTypeUrl: urls.length > 1 ? urls[1] : null
      } 
    } else {
      const convter = converters[key];
      newKey = convter ? convter(part[key]) : { ['others']: { ...obj['others'], [key]: part[key] } };
    }
    
    return {
      ...obj,
      ...newKey,
    }
  }, { coordinates });
}

function parsePart(subpartTitles) {
  const infoLists = subpartTitles.map(t => t.nextElementSibling);
  const infoElements = [].concat(...infoLists.map(ul => ul.querySelectorAll('li')))

  const props = infoElements
  .filter(li => li.text.includes(':'))
  .reduce((map, li) => {
    const [key] = li.text.split(':');
    const [_, value] = li.innerHTML.split(key);
    return { ...map, [key]: value.substr(2) }
  }, {})
  const others = infoElements
    .filter(li => !li.text.includes(':'))
    .map(li => li.innerHTML)
  return convertPart({
    ...props,
    others,
  })
}

const TITLES = ['Details', 'Localisation']
function parseMonoPartWindFarm(doc) {
  const subpartTitles = doc.querySelectorAll('h1')
    .filter(d => TITLES.includes(d.innerHTML))
  return [parsePart(subpartTitles)];
}

function parseMultiPartWindFarm(doc) {
  const partTitles = doc.querySelectorAll('h3');
  const titleByPart = groupBy(t => t.innerHTML, partTitles);
  return Object.values(titleByPart).map(parsePart);
}

async function getWindFarm(windFarm) {
  const res = await fetch(`${WIND_POWER_NET_BASE_URL}/${encodeURIComponent(windFarm.url)}`);
  const html = await res.text();
  const doc = parseHTML(html);

  const parts = windFarm.partCount > 1
    ? parseMultiPartWindFarm(doc)
    : parseMonoPartWindFarm(doc)

  // assert(parts.length === windFarm.partCount, 'Not matching part count')

  return {
    ...windFarm,
    parts,
  }
}

async function getAllWindFarms(countryId) {
  const filepath = `./_data/thewindpower_net/wind_farms/${countryId}.json`
  if (fs.existsSync(filepath)) return;

  const windFarmList = await getWindFarmList(countryId);

  let i = 0;
  const windFarms = await chunkAndChainPromises(windFarmList, w => {
    i += 1;
    if (i % 10 === 0) {
      console.log(countryId, i, windFarmList.length);
    }
    return getWindFarm(w)
  }, 10)

  fs.writeFileSync(filepath, JSON.stringify(windFarms))
}

const countryIds = [
  'AT',
  'BE',
  'BG',
  'CH',
  'CZ',
  'DK',
  'EE',
  'ES',
  'FR',
  'DE',
  'GB',
  'GR',
  'HU',
  'IE',
  'IT',
  'LT',
  'LU',
  'LV',
  'NL',
  'PL',
  'PT',
  'RO',
  'SE',
  'SI',
  'SK',
]

async function main() {
  // const countryIds = await getCountries();
  await chunkAndChainPromises(countryIds, getAllWindFarms, 1)
  console.log('DONE')
}

module.exports = {
  getAllWindFarms,
  getCountries,
}

if (require.main === module) {
  mkdirp.sync('./_data/thewindpower_net/wind_farms/')
  main();
}
