
document.addEventListener("DOMContentLoaded", function () {

    const configElement = document.getElementById(
        "limit-config"
    );

    const testSelect = document.getElementById(
        "test_key"
    );

    const fieldSelect = document.getElementById(
        "field_name"
    );

    const stageSelect = document.getElementById(
        "test_stage"
    );

    if (
        !configElement ||
        !testSelect ||
        !fieldSelect ||
        !stageSelect
    ) {
        return;
    }

    const limitConfig = JSON.parse(
        configElement.textContent
    );


    function updateLimitFields() {

        const selectedTest = testSelect.value;

        const testConfig = limitConfig[selectedTest];

        if (!testConfig) {
            return;
        }

        // Reset result field dropdown
        fieldSelect.replaceChildren();

        for (const [fieldName, fieldLabel]
            of Object.entries(testConfig.fields)) {

            fieldSelect.add(
                new Option(fieldLabel, fieldName)
            );
        }


        // Reset test stage dropdown
        stageSelect.replaceChildren();

        stageSelect.add(
            new Option("Normaal", "initial")
        );

        if (testConfig.has_afterstorage) {

            stageSelect.add(
                new Option(
                    "After storage",
                    "after_storage"
                )
            );
        }

    }


    testSelect.addEventListener(
        "change",
        updateLimitFields
    );

    updateLimitFields();

});
