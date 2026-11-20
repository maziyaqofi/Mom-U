const searchForm = document.getElementById("medication-search-form");
const searchInput = document.getElementById("medication-query");
const searchButton = document.getElementById("search-button");
const resultsSection = document.getElementById("search-results");
const resultsContainer = document.getElementById("results-container");

let activeVerificationToken = null;

function createElement(tag, className, text) {
    const element = document.createElement(tag);

    if (className) {
        element.className = className;
    }

    if (text !== undefined && text !== null) {
        element.textContent = text;
    }

    return element;
}

function showMessage(message, type = "info") {
    resultsContainer.replaceChildren();

    const messageElement = createElement(
        "div",
        `result-message ${type}`,
        message
    );

    resultsContainer.appendChild(messageElement);
    resultsSection.hidden = false;
}

function setLoading(isLoading) {
    searchButton.disabled = isLoading;
    searchButton.textContent = isLoading ? "Searching..." : "Search Medication";
}

function renderCandidates(data) {
    resultsContainer.replaceChildren();

    const heading = createElement(
        "h2",
        "results-heading",
        "Confirm Medication"
    );

    const description = createElement(
        "p",
        "results-description",
        "Please review and select the medication document(s) you want to retrieve."
    );

    resultsContainer.append(heading, description);

    const candidates = data.verification?.candidates || [];

    if (candidates.length === 0) {
        showMessage(
            "No matching medication candidates were found. Please check the medication name and try again.",
            "warning"
        );
        return;
    }

    const selectionForm = createElement("form", "candidate-form");
    selectionForm.id = "candidate-selection-form";

    candidates.forEach((candidate, candidateIndex) => {
        const candidateCard = createElement("div", "candidate-card");

        const candidateHeading = createElement(
            "h3",
            "candidate-name",
            candidate.name
        );

        const matchInfo = createElement(
            "p",
            "candidate-match",
            `Match type: ${candidate.match_type || "Not specified"}`
        );

        candidateCard.append(candidateHeading, matchInfo);

        (candidate.document_ids || []).forEach((documentId) => {
            const label = createElement("label", "candidate-option");
            const checkbox = createElement("input");

            checkbox.type = "checkbox";
            checkbox.name = "selected-document";
            checkbox.value = documentId;
            checkbox.dataset.candidateIndex = candidateIndex;

            const optionText = createElement(
                "span",
                "",
                `Document ID: ${documentId}`
            );

            label.append(checkbox, optionText);
            candidateCard.appendChild(label);
        });

        selectionForm.appendChild(candidateCard);
    });

    const confirmButton = createElement(
        "button",
        "confirm-button",
        "Confirm Selection"
    );

    confirmButton.type = "submit";
    selectionForm.appendChild(confirmButton);

    selectionForm.addEventListener("submit", handleConfirmation);

    resultsContainer.appendChild(selectionForm);
    resultsSection.hidden = false;
}

async function handleSearch(event) {
    event.preventDefault();

    const query = searchInput.value.trim();

    if (!query) {
        showMessage("Please enter a medication name.", "warning");
        searchInput.focus();
        return;
    }

    activeVerificationToken = null;
    setLoading(true);
    showMessage("Verifying medication candidates...", "info");

    try {
        const data = await MedicationAPI.verify(query);

        activeVerificationToken = data.verification_token || null;

        if (!activeVerificationToken) {
            showMessage(
                "No verification session was created. Please try another medication name.",
                "warning"
            );
            return;
        }

        renderCandidates(data);
    } catch (error) {
        showMessage(error.message, "error");
    } finally {
        setLoading(false);
    }
}

async function handleConfirmation(event) {
    event.preventDefault();

    if (!activeVerificationToken) {
        showMessage(
            "Your verification session is unavailable. Please search again.",
            "error"
        );
        return;
    }

    const selectedDocumentIds = Array.from(
        event.currentTarget.querySelectorAll(
            'input[name="selected-document"]:checked'
        )
    ).map((checkbox) => checkbox.value);

    if (selectedDocumentIds.length === 0) {
        showMessage(
            "Please select at least one medication document before confirming.",
            "warning"
        );
        return;
    }

    const confirmButton = event.currentTarget.querySelector(
        'button[type="submit"]'
    );

    confirmButton.disabled = true;
    confirmButton.textContent = "Retrieving Information...";

    try {
        const data = await MedicationAPI.confirm(
            activeVerificationToken,
            selectedDocumentIds
        );

        activeVerificationToken = null;
        renderMedicationRecords(data.records || []);
    } catch (error) {
        confirmButton.disabled = false;
        confirmButton.textContent = "Confirm Selection";
        showMessage(error.message, "error");
    }
}

function renderMedicationRecords(records) {
    resultsContainer.replaceChildren();

    if (records.length === 0) {
        showMessage(
            "No medication information was returned for the selected documents.",
            "warning"
        );
        return;
    }

    const heading = createElement(
        "h2",
        "results-heading",
        "Medication Information"
    );

    const description = createElement(
        "p",
        "results-description",
        `${records.length} medication record(s) retrieved successfully.`
    );

    resultsContainer.append(heading, description);

    records.forEach((record) => {
        const card = createElement("article", "medication-card");

        const name = createElement(
            "h3",
            "medication-name",
            record.medication_name || "Unknown medication"
        );

        const documentId = createElement(
            "p",
            "medication-document-id",
            `Document ID: ${record.document_id || "Not available"}`
        );

        const category = createElement("div", "medication-category");

        category.append(
            createElement("span", "field-label", "Pregnancy Category"),
            createElement(
                "strong",
                "category-value",
                record.pregnancy_category || "Not specified"
            )
        );

        const safetySection = createElement("section", "safety-section");

        safetySection.appendChild(
            createElement("h4", "", "Safety Statement")
        );

        if (record.safety_statement_available && record.safety_statement) {
            safetySection.appendChild(
                createElement("p", "safety-statement", record.safety_statement)
            );
        } else {
            safetySection.appendChild(
                createElement(
                    "p",
                    "safety-unavailable",
                    "No safety statement is available in this record. This does not mean the medication is safe during pregnancy."
                )
            );
        }

        const classificationSection = createElement(
            "section",
            "classification-section"
        );

        classificationSection.appendChild(
            createElement("h4", "", "Medication Classification")
        );

        const classifications = [
            record.classification_1,
            record.classification_2,
            record.classification_3,
        ].filter(Boolean);

        classificationSection.appendChild(
            createElement(
                "p",
                "classification-value",
                classifications.length
                    ? classifications.join(" / ")
                    : "Not specified"
            )
        );

        const source = createElement(
            "p",
            "medication-source",
            `Source: ${record.source || "Not specified"}`
        );

        card.append(
            name,
            documentId,
            category,
            safetySection,
            classificationSection,
            source
        );

        resultsContainer.appendChild(card);
    });

    const disclaimer = createElement(
        "p",
        "medical-disclaimer",
        "Important: MOM-U provides retrieved medication information for educational and research purposes. This information is not a diagnosis, prescription, or individualized medical recommendation. Pregnancy category and retrieved safety statements should not be interpreted as a guarantee of safety. Always consult a qualified healthcare professional."
    );

    resultsContainer.appendChild(disclaimer);
    resultsSection.hidden = false;
}

searchForm.addEventListener("submit", handleSearch);
