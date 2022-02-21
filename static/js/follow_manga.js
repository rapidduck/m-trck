async function send_follow_request(manga) {
    console.log("before ready");
    let sw = await navigator.serviceWorker.ready;
    console.log("after ready");

    let push = await sw.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey:
        'BFHeG_-cgzrK3xohv4poJ7z4tpX9oDROrj8Rj3fXCjpuuK8pKdNSmF5T2rKKEY0lammQ_2_f1t_NGyG0RqOuynk'
    });

    push_data = JSON.stringify(push);
    console.log(push_data);

    manga = JSON.stringify(manga);
    console.log(manga);
    const Http = new XMLHttpRequest();
    const url = "/follow?manga=".concat(manga).concat("&endpoint=").concat(push_data);
    console.log(url);
    Http.open("POST", url);
    Http.send();


}