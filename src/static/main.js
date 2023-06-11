const navBtn = document.querySelector("#nav-btn");
const closeBtn = document.querySelector("#close-btn");
const sidebar = document.querySelector("#sidebar");
const date = document.querySelector("#date");

// show sidebar
navBtn.addEventListener("click", function () {
  sidebar.classList.add("show-sidebar");
});
closeBtn.addEventListener("click", function () {
  sidebar.classList.remove("show-sidebar");
});
// set year
date.innerHTML = new Date().getFullYear();

/* 
==========
Dialog box
========== 
*/
function myConfirmBox(message) {
  let element = document.createElement("div");
  element.classList.add("dialog-background");
  element.innerHTML = `<div class="dialog">
                            <h3>${message}</h3>
                            <div>
                                <button id="trueButton" class="btn btn-primary">Yes</button> <!-- Set Id for both buttons -->
                                <button id="falseButton" class="btn btn-secondary">No</button>
                            </div>
                        </div>`;
  document.body.appendChild(element);
  return new Promise(function (resolve, reject) {
    document
      .getElementById("trueButton")
      .addEventListener("click", function () {
        resolve(true);
        document.body.removeChild(element);
      });
    document
      .getElementById("falseButton")
      .addEventListener("click", function () {
        resolve(false);
        document.body.removeChild(element);
      });
  });
}

// Logout listener pc version
document.getElementById("logout-btn-id").addEventListener("click", () => {
  myConfirmBox("Are you sure you want to log out?").then((response) => {
    if (response) {
      window.location.replace("http://127.0.0.1:8000/account/logout/");
    }
  });
});

// Logout listener phone version
document
  .getElementById("logout-btn-id-2")
  .addEventListener("click", (event) => {
    event.preventDefault(); // Prevent the default link behavior
    sidebar.classList.remove("show-sidebar");
    myConfirmBox("Are you sure you want to log out?").then((response) => {
      if (response) {
        window.location.href = "http://127.0.0.1:8000/account/logout/";
      }
    });
  });
