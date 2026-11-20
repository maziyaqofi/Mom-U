const API_BASE_URL = "";

async function apiRequest(endpoint, payload) {
    let response;

    try {
        response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });
    } catch (error) {
        throw new Error(
            "Unable to connect to MOM-U server. Please check your connection."
        );
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        const message =
            typeof data?.detail === "string"
                ? data.detail
                : `Request failed with status ${response.status}.`;

        throw new Error(message);
    }

    return data;
}

const MedicationAPI = {
    resolve(query) {
        return apiRequest("/api/medications/resolve", {
            query,
        });
    },

    verify(query) {
        return apiRequest("/api/medications/verify", {
            query,
        });
    },

    confirm(verificationToken, selectedDocumentIds) {
        return apiRequest("/api/medications/confirm", {
            verification_token: verificationToken,
            selected_document_ids: selectedDocumentIds,
        });
    },
};

window.MedicationAPI = MedicationAPI;
