function getCertificate () {

  let xhr = new XMLHttpRequest(),
    studentNumberEl = document.querySelectorAll('[name=student_number]')[0],
    studentNumber = studentNumberEl.value,
    nameEl = document.querySelectorAll('[name=name]')[0],
    name = nameEl.value;
  xhr.open('GET', '/certificate/' + studentNumber + '/' + name);
  xhr.send(null);

  xhr.onreadystatechange = function () {
    var DONE = 4; // readyState 4 means the request is done.
    var OK = 200; // status 200 is a successful return.
    if (xhr.readyState === DONE) {
      if (xhr.status === OK) {
        document.getElementById('cert-container').innerHTML = xhr.response;
      } else {
        console.log('Error: ' + xhr.status);
      }
    }
  };

}
