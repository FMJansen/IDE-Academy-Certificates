function getCertificate () {

  let xhr = new XMLHttpRequest(),
    nameEl = document.querySelectorAll('[name=name]')[0],
    name = nameEl.value,
    formStatus = document.getElementById('form-status'),
    certContainer = document.getElementById('cert-container');

  formStatus.innerHTML = "";
  xhr.open('GET', '/certificate/' + name);
  xhr.send(null);

  xhr.onreadystatechange = function () {
    var DONE = 4; // readyState 4 means the request is done.
    var OK = 200; // status 200 is a successful return.
    if (xhr.readyState === DONE) {
      if (xhr.status === OK) {
        if (xhr.response === "404") {
          formStatus.innerHTML = "seems like you didn’t attend any workshops yet, sorry";
        } else {
          certContainer.innerHTML = xhr.response;
          certContainer.className += " show"
        }
      } else {
        console.log('Error: ' + xhr.status);
      }
    }
  };

}
