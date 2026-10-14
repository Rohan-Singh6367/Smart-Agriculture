
"use strict";

/* =========================================================
   SMART AGRICULTURE AI
   COMPLETE JAVASCRIPT
========================================================= */


/* =========================================================
   HELPER FUNCTIONS
========================================================= */

function getElement(id) {

    return document.getElementById(id);

}


function setLoading(element, isLoading) {

    if (!element) return;

    element.hidden = !isLoading;

}


function setResult(element, message, isError = false) {

    if (!element) return;

    element.textContent = message || "";

    element.classList.toggle("error-result", isError);

}


function formatWeather(data) {

    return [
        `🌍 City: ${data.city || "Unknown"}`,
        `🌡️ Temperature: ${data.temperature ?? "N/A"} °C`,
        `💧 Humidity: ${data.humidity ?? "N/A"}%`,
        `🌡️ Feels Like: ${data.feels_like ?? "N/A"} °C`,
        `🌧️ Precipitation: ${data.precipitation ?? "N/A"} mm`,
        `💨 Wind Speed: ${data.wind_speed ?? "N/A"} km/h`,
        `☁️ Condition: ${data.description || "Unknown"}`
    ].join("\n");

}


function formatPrice(data) {

    return [
        `🌾 Crop: ${data.crop || "N/A"}`,
        `📍 State: ${data.state || "N/A"}`,
        `🌱 Season: ${data.season || "N/A"}`,
        `📅 Month: ${data.month || "N/A"}`,
        `💰 Predicted Price: ${data.price ?? "N/A"}`
    ].join("\n");

}


/* =========================================================
   AI CHATBOT
========================================================= */

const chatInput = getElement("chatInput");
const sendChatBtn = getElement("sendChatBtn");
const chatMessages = getElement("chatMessages");
const languageSelect = getElement("language");
const chatLoading = getElement("chatLoading");


function addChatMessage(message, sender = "bot") {

    const messageDiv = document.createElement("div");

    messageDiv.className =
        sender === "user"
            ? "user-message"
            : "bot-message";

    messageDiv.textContent = message;

    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;

}


async function sendChatMessage() {

    const message = chatInput.value.trim();

    const language = languageSelect.value;

    if (!message) {

        return;

    }

    addChatMessage(message, "user");

    chatInput.value = "";

    sendChatBtn.disabled = true;

    setLoading(chatLoading, true);

    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                message: message,

                language: language

            })

        });


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.reply ||
                data.message ||
                "Chat request failed."
            );

        }


        addChatMessage(

            data.reply ||
            "Sorry, no response received."

        );


    } catch (error) {

        console.error("Chat Error:", error);

        addChatMessage(

            "Unable to connect to the AI service. Please try again."

        );

    } finally {

        sendChatBtn.disabled = false;

        setLoading(chatLoading, false);

        chatInput.focus();

    }

}


sendChatBtn.addEventListener(

    "click",

    sendChatMessage

);


chatInput.addEventListener(

    "keydown",

    function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendChatMessage();

        }

    }

);


/* =========================================================
   AI CROP DISEASE DETECTION
========================================================= */

const cropImage = getElement("cropImage");

const imagePreview = getElement("imagePreview");

const detectDiseaseBtn = getElement("detectDiseaseBtn");

const diseaseLoading = getElement("diseaseLoading");

const diseaseResult = getElement("diseaseResult");

let selectedCropImage = null;


/* =========================================================
   IMAGE PREVIEW
========================================================= */

cropImage.addEventListener(

    "change",

    function () {

        const file = this.files[0];

        selectedCropImage = null;

        setResult(diseaseResult, "");

        imagePreview.hidden = true;

        if (!file) {

            return;

        }


        const allowedTypes = [

            "image/jpeg",

            "image/png",

            "image/webp"

        ];


        if (!allowedTypes.includes(file.type)) {

            setResult(

                diseaseResult,

                "Please select a JPG, PNG, or WEBP image.",

                true

            );

            cropImage.value = "";

            return;

        }


        if (file.size > 5 * 1024 * 1024) {

            setResult(

                diseaseResult,

                "Image size must be less than 5 MB.",

                true

            );

            cropImage.value = "";

            return;

        }


        selectedCropImage = file;


        const imageURL = URL.createObjectURL(file);

        imagePreview.src = imageURL;

        imagePreview.hidden = false;


        imagePreview.onload = function () {

            URL.revokeObjectURL(imageURL);

        };

    }

);


/* =========================================================
   DETECT DISEASE
========================================================= */

detectDiseaseBtn.addEventListener(

    "click",

    async function () {

        if (!selectedCropImage) {

            setResult(

                diseaseResult,

                "Please select a crop image first.",

                true

            );

            return;

        }


        const formData = new FormData();

        formData.append("image", selectedCropImage);


        detectDiseaseBtn.disabled = true;

        setLoading(diseaseLoading, true);

        setResult(diseaseResult, "");


        try {

            const response = await fetch(

                "/detect-disease",

                {

                    method: "POST",

                    body: formData

                }

            );


            const data = await response.json();


            if (!response.ok || !data.success) {

                throw new Error(

                    data.message ||

                    "Unable to analyze image."

                );

            }


            setResult(

                diseaseResult,

                data.reply ||

                "No analysis result received."

            );


        } catch (error) {

            console.error(

                "Disease Detection Error:",

                error

            );


            setResult(

                diseaseResult,

                error.message ||

                "Something went wrong. Please try again.",

                true

            );

        } finally {

            detectDiseaseBtn.disabled = false;

            setLoading(diseaseLoading, false);

        }

    }

);


/* =========================================================
   LIVE WEATHER
========================================================= */

const cityInput = getElement("cityInput");

const getWeatherBtn = getElement("getWeatherBtn");

const weatherLoading = getElement("weatherLoading");

const weatherResult = getElement("weatherResult");


async function getWeather() {

    const city = cityInput.value.trim();


    if (!city) {

        setResult(

            weatherResult,

            "Please enter a city.",

            true

        );

        return;

    }


    getWeatherBtn.disabled = true;

    setLoading(weatherLoading, true);

    setResult(weatherResult, "");


    try {

        const response = await fetch(

            "/weather",

            {

                method: "POST",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify({

                    city: city

                })

            }

        );


        const data = await response.json();


        if (!response.ok || !data.success) {

            throw new Error(

                data.message ||

                "Unable to get weather."

            );

        }


        setResult(

            weatherResult,

            formatWeather(data)

        );


    } catch (error) {

        console.error(

            "Weather Error:",

            error

        );


        setResult(

            weatherResult,

            error.message ||

            "Unable to connect to weather service.",

            true

        );

    } finally {

        getWeatherBtn.disabled = false;

        setLoading(weatherLoading, false);

    }

}


getWeatherBtn.addEventListener(

    "click",

    getWeather

);


cityInput.addEventListener(

    "keydown",

    function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            getWeather();

        }

    }

);


/* =========================================================
   CROP PRICE PREDICTION
========================================================= */

const cropSelect = getElement("cropSelect");

const stateSelect = getElement("stateSelect");

const seasonSelect = getElement("seasonSelect");

const monthSelect = getElement("monthSelect");

const predictPriceBtn = getElement("predictPriceBtn");

const priceLoading = getElement("priceLoading");

const priceResult = getElement("priceResult");


async function predictCropPrice() {

    const crop = cropSelect.value;

    const state = stateSelect.value;

    const season = seasonSelect.value;

    const month = monthSelect.value;


    if (!crop || !state || !season || !month) {

        setResult(

            priceResult,

            "Please fill in all crop details.",

            true

        );

        return;

    }


    predictPriceBtn.disabled = true;

    setLoading(priceLoading, true);

    setResult(priceResult, "");


    try {

        const response = await fetch(

            "/predict-price",

            {

                method: "POST",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify({

                    crop: crop,

                    state: state,

                    season: season,

                    month: Number(month)

                })

            }

        );


        const data = await response.json();


        if (!response.ok || !data.success) {

            throw new Error(

                data.message ||

                "Unable to predict price."

            );

        }


        setResult(

            priceResult,

            formatPrice(data)

        );


    } catch (error) {

        console.error(

            "Price Prediction Error:",

            error

        );


        setResult(

            priceResult,

            error.message ||

            "Unable to predict price.",

            true

        );

    } finally {

        predictPriceBtn.disabled = false;

        setLoading(priceLoading, false);

    }

}


predictPriceBtn.addEventListener(

    "click",

    predictCropPrice

);