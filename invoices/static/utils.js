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