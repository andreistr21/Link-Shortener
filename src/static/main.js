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
      const currentLocation = location.protocol + "//" + location.host;
      window.location.replace(currentLocation + "/account/logout/");
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
        const currentLocation = location.protocol + "//" + location.host;
        window.location.href = currentLocation + "/account/logout/";
      }
    });
  });

// Link deletion listener
document
  .getElementById("link-delete-btn-id")
  .addEventListener("click", (event) => {
    const alias = window.location.href.split("/").slice(-2)[0];
    event.preventDefault(); // Prevent the default link behavior
    myConfirmBox("Are you sure you want to delete this link?").then(
      (response) => {
        if (response) {
          const currentLocation = location.protocol + "//" + location.host;
          window.location.replace(
            currentLocation + "/account/link/delete/" + alias + "/"
          );
        }
      }
    );
  });

/* 
==========
Sorting dropdown menu
========== 
*/
/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function dropdownClick() {
  document
    .getElementById("dropdown-click-content-id")
    .classList.toggle("show-dropdown-click");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function (event) {
  if (
    !event.target.matches(".drop-btn-click") &&
    !event.target.closest(".drop-btn-click")
  ) {
    // sourcery skip: avoid-using-var
    var dropdowns = document.getElementsByClassName("dropdown-click-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains("show-dropdown-click")) {
        openDropdown.classList.remove("show-dropdown-click");
      }
    }
  }
};
