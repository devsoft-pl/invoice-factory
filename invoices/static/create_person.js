document.addEventListener("DOMContentLoaded", function () {
    const createPersonButton = document.getElementById('createPersonButton');

    const personModalElement = document.getElementById('personModal');
    const personModalContentElement = document.getElementById('personModalContent');

    const url = createPersonButton.getAttribute("href");

    personModalElement.addEventListener('hidden.bs.modal', function (event) {
      personModalContentElement.innerHTML = ''
    })

    createPersonButton.addEventListener("click", async (e) => {
        e.preventDefault();

        const response = await fetch(url);
        const data = await response.text();

        personModalContentElement.innerHTML = data;

        const modal = new bootstrap.Modal(personModalElement, {});
        modal.show();

        const selectCountryElement = document.getElementById("id_country");

        const optionCountryElement = createCountryOptionElement("new_country", "Dodaj nowy kraj", true);
        selectCountryElement.appendChild(optionCountryElement);

        const cancelCountryElement = document.getElementById("cancelCountryButton");
        const saveCountryElement = document.getElementById("saveCountryButton");
        console.log(cancelCountryElement)

        const newCountryInput = document.createElement("input");
        newCountryInput.classList.add("form-control");

        selectCountryElement.addEventListener("change", () => {
            if (selectCountryElement.value === "new_country") {
                cancelCountryElement.classList.remove("d-none");
                saveCountryElement.classList.remove("d-none");
                selectCountryElement.classList.add("d-none");
                selectCountryElement.parentElement.appendChild(newCountryInput);
                newCountryInput.classList.remove("d-none");
            }
        });

        const hideCountryEditMode = () => {
            cancelCountryElement.classList.add("d-none");
            saveCountryElement.classList.add("d-none");
            newCountryInput.classList.add("d-none")
            selectCountryElement.classList.remove("d-none");
        };

        cancelCountryElement.addEventListener("click", (e) => {
            e.preventDefault();
            hideCountryEditMode();
            selectCountryElement.value = "";
            newCountryInput.value = "";
        });

        saveCountryElement.addEventListener("click", async (e) => {
            e.preventDefault();
            hideCountryEditMode();

            const urlCountry = saveCountryElement.getAttribute("href");
            const csrfCountryElement = document.getElementsByName("csrfmiddlewaretoken")[0];

            const data = new FormData();
            data.set("country", newCountryInput.value)
            data.set("csrfmiddlewaretoken", csrfCountryElement.value)

            const response = await fetch(urlCountry, {
                method: "POST",
                body: data
            });
            const json = await response.json();

            const newCountryOption = createCountryOptionElement(json.id, json.name);
            selectCountryElement.appendChild(newCountryOption);

            selectCountryElement.value = json.id.toString();
            newCountryInput.value = "";
        });

        const createPersonSaveButton = document.getElementById('createPersonSaveButton');

        createPersonSaveButton.addEventListener("click", async (e) => {
            e.preventDefault();

            const form = personModalContentElement.getElementsByTagName('form')[0]
            const data = new FormData(form)

            const response = await fetch(url, {
                method: "POST",
                body: data
            });

            const json = await response.json();

            if (json.success) {
                const selectElement = document.getElementById('id_person');

                const optionElement = document.createElement('option');
                optionElement.setAttribute('value', json.id);

                const optionNameElement = document.createTextNode(json.name);

                optionElement.appendChild(optionNameElement)
                selectElement.appendChild(optionElement);

                selectElement.value = json.id.toString()

                modal.hide();
            }
        })
    });
});