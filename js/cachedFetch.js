var filename = 'cachedFetch.js';

// Need to import localforage:
// https://cdnjs.cloudflare.com/ajax/libs/localforage/1.4.0/localforage.min.js
function cachedFetch(url, expireTime = 3600000) {
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

function getCachedTime(url) {
  console.log(filename + ": Getting " + url + " acquired time.");
  return localforage.getItem(url).then(function(value){
    if(value == null) {
      console.log(filename + ": " + url + " timestamp just created. Return current time.")
      return Date.now();
    } else {
      console.log(filename + ": " + url + " cached timestamp found and will be returned.")
      return value.updated;
    }
  })
}

async function blocking_cachedFetch(url, expireTime = 3600000) {
  var obj = await cachedFetch(url, expireTime);
  return obj;
}

function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}


