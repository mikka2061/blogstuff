var appToken = '';

// Setup micro.blog API and content 
var endpoint = "https://micro.blog/micropub"
var content = CONTENT_FROM_SOMEWHERE

// create and post HTTP request
var http = HTTP.create();
var response = http.request({
  "url": endpoint,
  "method": "POST",
  "encoding": "form",
  "data": {
    "h": "entry",
    "content": content
  },
  "headers": {
    "Authorization": "Bearer " + appToken
  }
});

console.log("Response: " + response.statusCode);

if (response.statusCode != 200 && response.statusCode != 202) {
  context.fail();
}