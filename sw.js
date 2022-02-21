self.addEventListener('push', function(e) {
  var body;

  if (e.data) {
    var data = JSON.parse(e.data.text());
    body = data["body"];
    title = data["title"];
  } else {
    body = 'Push message no payload';
    title = "NO GODDAMN TITLE";
  }

  var options = {
    body: body,
    icon: 'komi.jpg',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '2'
    },
    actions: [
      {action: 'Like', title: 'Button 1',
        icon: 'images/checkmark.png'},
      {action: 'Close', title: 'Button 2',
        icon: 'images/xmark.png'},
    ]
  };
  e.waitUntil(
    self.registration.showNotification(title, options)
  );
});