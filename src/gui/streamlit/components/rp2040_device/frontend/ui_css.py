# src/gui/streamlit/components/rp2040_device/frontend/ui_css.py

CSS = """
.rp2040-device {
    width: 100%;
    font-family: var(--st-font);
}

.field {
    margin-bottom: 1rem;
}

.field label {
    display: block;
    margin-bottom: 0.35rem;
    font-weight: 600;
}

.button-row {
    display: flex;
    gap: 0.5rem;
}

button {
    padding: 0.5rem 1rem;
    cursor: pointer;
}

button:disabled {
    cursor: not-allowed;
    opacity: 0.5;
}

button.primary {
    background: var(--st-primary-color);
    color: white;
    border: none;
    border-radius: 0.4rem;
}

input[type="text"] {
    width: 100%;
    box-sizing: border-box;
    padding: 0.5rem;
}

progress {
    width: 100%;
    height: 1rem;
}

#file-list {
    margin-top: 0.5rem;
    border: 1px solid rgba(128, 128, 128, 0.25);
    border-radius: 0.4rem;
    padding: 0.5rem;
    min-height: 4rem;
}

.file-entry {
    padding: 0.25rem;
}

.directory-entry {
    font-weight: 600;
    cursor: pointer;
}

#status,
#device-status,
#progress-text,
#selected-file,
#current-directory {
    margin-top: 0.35rem;
    font-size: 0.9rem;
}
"""