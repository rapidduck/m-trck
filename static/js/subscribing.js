async function subscribe(id) {
  console.log("before ready");
    let sw = await navigator.serviceWorker.ready;
    console.log("after ready");
    let push = await sw.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey:
        'BFHeG_-cgzrK3xohv4poJ7z4tpX9oDROrj8Rj3fXCjpuuK8pKdNSmF5T2rKKEY0lammQ_2_f1t_NGyG0RqOuynk'
    });
    console.log(JSON.stringify(push));
    query = "channel_id=".concat(id).concat("&data=".concat(JSON.stringify(push)));
    console.log(query);
    const Http = new XMLHttpRequest();
    const url= "{{url_for("save_endpoint")}}?".concat(query);
    console.log(url);
    Http.open("POST", url);

    Http.send();
  }

