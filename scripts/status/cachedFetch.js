var filename = 'cachedFetch.js';

// Need to import localforage:
// https://cdnjs.cloudflare.com/ajax/libs/localforage/1.4.0/localforage.min.js
function cachedFetch(url, expireTime = 360000) {
  console.log(filename + ": Checking " + url);
  return localforage.getItem(url).then(function(value){
    // create new cache if expired or empty (time is in ms)
    if (value == null || Date.now() - value.updated > expireTime){
      console.log(filename + ": Getting " + url + " from internet (it might be time-consuming.)")
      return fetch(url)
        .then(function(result){
          return result.json();
        })
        .then(function(value){
          return localforage.setItem(url, {'updated': Date.now(), 'data': value})
            .then(function(entry){
              return entry['data'];
            })
        })
    } else {
      console.log(filename + ": Getting " + url + " from cache")
      return localforage.getItem(url)
        .then(function(entry){
          return entry['data'];
        })
    }
  })
}