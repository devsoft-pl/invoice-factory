const createCountryOptionElement = (value, label, color = false) => {
            const optionElement = document.createElement("option");
            optionElement.setAttribute("value", value);
            if (color) {
                optionElement.style.color = "red";
            }

            const createTextElement = document.createTextNode(label);
            optionElement.appendChild(createTextElement);

            return optionElement;
        }

const isLastDayOfMonth = (currentDate) =>{
    const [day, month, year] = currentDate.split('.').map(Number);
    const givenDate = new Date(year, month - 1, day);
    const nextMonthDate = new Date(year, month, 1);
    const lastDayOfMonth = new Date(nextMonthDate - 1);
    return givenDate.getDate() === lastDayOfMonth.getDate();
}

const isLastDay = (currentDay) =>{
    if (typeof currentDay !== 'number' || currentDay < 0 || currentDay > 31) {
        return false;
    }
    return [28, 29, 30, 31].includes(currentDay);
}

const createFormErrors = (fieldName, errors) => {
        const selectElement = document.getElementById("id_" + fieldName);
        const rowContainer = selectElement.parentElement.parentElement;

        const errorElement = document.createElement('div');
        errorElement.setAttribute('id', 'id_' + fieldName + '_errors');
        errorElement.setAttribute('class', 'row');

        const errorContainer = document.createElement('div');
        errorContainer.setAttribute('class', 'col-12 offset-md-6 text-danger');
        errorElement.appendChild(errorContainer);

        const errorUlContainer = document.createElement('ul');
        errorUlContainer.setAttribute('class', 'errorlist');
        errorContainer.appendChild(errorUlContainer);

        if (errors.hasOwnProperty(fieldName)) {
            const fieldErrors = errors[fieldName];

            fieldErrors.forEach((value) => {
                const errorLiElement = document.createElement('li');
                const errorLabel = document.createTextNode(value);
                errorLiElement.appendChild(errorLabel);

                errorUlContainer.appendChild(errorLiElement);
            });

            rowContainer.parentElement.insertBefore(errorElement, rowContainer.nextSibling);
        }
    }