const { splitEvery } = require('ramda');

function chunkAndChainPromises(data, dataToPromiseFn, chunkSize) {
  return splitEvery(chunkSize, data).reduce((last, items) => {
    return last.then(array => {
      return Promise.all(items.map(dataToPromiseFn)).then(values => {
        return array.concat(values);
      });
    });
  }, Promise.resolve([]));
}

module.exports = {
  chunkAndChainPromises,
}