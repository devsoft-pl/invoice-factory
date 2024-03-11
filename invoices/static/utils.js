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