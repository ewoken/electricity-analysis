const fs = require('fs');
const mkdirp = require('mkdirp')

const fetch = require('isomorphic-fetch');
const { parse: parseHTML } = require('node-html-parser'); 

const { chunkAndChainPromises } = require('./helpers');

const WIND_POWER_NET_BASE_URL = 'https://www.thewindpower.net/'

async function getManufacturerUrls() {
  const res = await fetch(`${WIND_POWER_NET_BASE_URL}/turbines_manufacturers_en.php`);
  const html = await res.text();
  const doc = parseHTML(html);
  
  const links = doc.querySelectorAll('table a.lien_standard_tab');
  return links
    .map(link => link.getAttribute('href'))
    .filter(url => url.startsWith('manufacturer'));
}

async function getManufacturerTurbineUrls(manufacturerUrl) {
  const res = await fetch(`${WIND_POWER_NET_BASE_URL}/${manufacturerUrl}`);
  const html = await res.text();
  const doc = parseHTML(html);

  const links = doc.querySelectorAll('li a');
  return links
    .map(link => link.getAttribute('href'))
    .filter(url => url.startsWith('turbine_'));
}

async function getAllTurbineUrls() {
  const manufacturerUrls = await getManufacturerUrls();

  let i = 0;
  const turbineUrlByManufacturer = await chunkAndChainPromises(manufacturerUrls, manufacturerUrl => {
    i += 1;
    if (i % 10 === 0) {
      console.log(i, manufacturerUrls.length);
    }
    return getManufacturerTurbineUrls(manufacturerUrl);
  }, 5);

  return [].concat(...turbineUrlByManufacturer);
}

function convertNumber(v) {
  return v ? Number(v.split(' ')[0].replace(',', '')) : null
}

function parseLoadingCurve(s) {
  const arrayString = s.match(/(\['[0-9.]{1,4}',\s*\d+\],)+/g)[0];
  const withoutTrailingComma = arrayString.endsWith(',') ? arrayString.substr(0, arrayString.length - 1) : arrayString;
  const array = JSON.parse('[' + withoutTrailingComma.replace(/'/g, '"') + ']');

  return array.map(a => a[1]);
}

async function getTurbine(turbineUrl) {
  const res = await fetch(`${WIND_POWER_NET_BASE_URL}/${turbineUrl}`);
  const html = await res.text();
  const doc = parseHTML(html);

  const infoElements = doc.querySelectorAll('table li');

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

  const info = {
    ...props,
    others,
  }
  const links = doc.querySelectorAll('li a');
  const chartScript = doc.querySelectorAll('script').map(s => s.innerHTML).find(s => s.includes('google.charts.Bar'));
  const loadingCurve = chartScript ? parseLoadingCurve(chartScript) : null 

  const turbine = {
    url: turbineUrl,
    manufacturerUrl: links.map(a => a.getAttribute('href')).find(url => url.startsWith('manufacturer')),
    power_kW: convertNumber(info['Rated power']),
    rotorDiameter: convertNumber(info['Rotor diameter']),
    isOffshore: info['Offshore model'] ? info['Offshore model'] === 'yes' : null,
    cutInSpeed: convertNumber(info['Cut-in wind speed']),
    ratedSpeed: convertNumber(info['Rated wind speed']),
    cutOffSpeed: convertNumber(info['Cut-off wind speed']),
    loadingCurve,
  }

  return turbine
}

async function getAllTurbines() {
  const turbineUrls = await getAllTurbineUrls();

  let i = 0;
  const turbines = await chunkAndChainPromises(turbineUrls, turbineUrl => {
    i += 1;
    if (i % 10 === 0) {
      console.log(i, turbineUrls.length);
    }
    return getTurbine(turbineUrl);
  }, 10)

  return turbines;
}

async function main() {
  const turbines = await getAllTurbines();

  mkdirp.sync('./_data/thewindpower_net/')
  fs.writeFileSync('./_data/thewindpower_net/world_turbines.json', JSON.stringify(turbines));
  console.log('DONE');
}

if (require.main === module) {
  main();
}