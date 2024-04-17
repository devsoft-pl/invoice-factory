const createOptionElement = (value, label, color = false) => {
    const optionElement = document.createElement("option");
    optionElement.setAttribute("value", value);
    if (color) {
        optionElement.style.color = "red";
    }

    const createTextElement = document.createTextNode(label);
    optionElement.appendChild(createTextElement);

    return optionElement;
}

document.addEventListener("DOMContentLoaded", () => {
    const selectElement = document.getElementById("id_country");

    const optionElement = createOptionElement("new_country", "Dodaj nowy kraj", true);
    selectElement.appendChild(optionElement);

    const cancelElement = document.getElementById("cancelCountryButton");
    const saveElement = document.getElementById("saveCountryButton");

    const newCountryInput = document.createElement("input");
    newCountryInput.classList.add("form-control");

    selectElement.addEventListener("change", () => {
        if (selectElement.value === "new_country") {
            cancelElement.classList.remove("d-none");
            saveElement.classList.remove("d-none");
            selectElement.classList.add("d-none");
            selectElement.parentElement.appendChild(newCountryInput);
            newCountryInput.classList.remove("d-none");
        }
    });

    const hideEditMode = () => {
        cancelElement.classList.add("d-none");
        saveElement.classList.add("d-none");
        newCountryInput.classList.add("d-none");
        selectElement.classList.remove("d-none");
    };

    cancelElement.addEventListener("click", (e) => {
        e.preventDefault();
        hideEditMode();
        selectElement.value = "";
        newCountryInput.value = "";
    });

    saveElement.addEventListener("click", async (e) => {
        e.preventDefault();

        const countryErrors = document.getElementById('id_country_errors');
        if (countryErrors) {
            countryErrors.parentElement.removeChild(countryErrors);
        }

        const url = saveElement.getAttribute("href");
        const csrfElement = document.getElementsByName("csrfmiddlewaretoken")[0];

        const data = new FormData();
        data.set("country", newCountryInput.value);
        data.set("csrfmiddlewaretoken", csrfElement.value);

        const response = await fetch(url, {
            method: "POST",
            body: data
        });

        const json = await response.json();

        if (json['success'] === false) {
            const rowContainer = selectElement.parentElement.parentElement;

            const errorElement = document.createElement('div');
            errorElement.setAttribute('id', 'id_country_errors');
            errorElement.setAttribute('class', 'row');

            const errorContainer = document.createElement('div');
            errorContainer.setAttribute('class', 'col-auto offset-5 text-danger');
            errorElement.appendChild(errorContainer);

            const errorUlContainer = document.createElement('ul');
            errorUlContainer.setAttribute('class', 'errorlist');
            errorContainer.appendChild(errorUlContainer);

            const countryErrors = json['errors']['country'];

            countryErrors.forEach((value) => {
                const errorLiElement = document.createElement('li');
                const errorLabel = document.createTextNode(value);
                errorLiElement.appendChild(errorLabel);

                errorUlContainer.appendChild(errorLiElement);
            });

            rowContainer.parentElement.insertBefore(errorElement, rowContainer.nextSibling);
        } else {
            hideEditMode();

            const newCountryOption = createOptionElement(json.id, json.name);
            selectElement.appendChild(newCountryOption);

            selectElement.value = json.id.toString();
            newCountryInput.value = "";
        }
    });
});
