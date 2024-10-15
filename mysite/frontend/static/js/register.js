
document.addEventListener('DOMContentLoaded', function() {
    const checkbox = document.getElementById('terms');
    const termsLabel = document.querySelector('label[for="terms"]'); // Select the label for the checkbox
    const termsLink = termsLabel.querySelector('a');
    // Get computed styles of the document
    const rootStyles = getComputedStyle(document.documentElement);

    // Fetch the custom property values (CSS variables)
    const highlightColor = rootStyles.getPropertyValue('--primary-color');
    const fadedColor = rootStyles.getPropertyValue('--hover-color');
    const hoverColor = 'blue';

    // Initial state - apply the highlight color if unchecked
    if (!checkbox.checked) {
        termsLabel.style.color = highlightColor;
        termsLink.style.color = highlightColor;
    }

    // Add event listener to the checkbox to track changes
    checkbox.addEventListener('change', function() {
        if (checkbox.checked) {
            termsLabel.style.color = fadedColor; // Apply the faded color
            termsLink.style.color = fadedColor;
        } else {
            termsLabel.style.color = highlightColor; // Apply the highlight color
            termsLink.style.color = highlightColor; // Apply the highlight color
        }
    });

    // Add event listeners for hover effect on the link
    termsLink.addEventListener('mouseenter', function() {
        termsLink.style.color = hoverColor; // Change color on hover
    });

    termsLink.addEventListener('mouseleave', function() {
        if (checkbox.checked) {
            termsLink.style.color = fadedColor; // Revert to faded color if checkbox is checked
        } else {
            termsLink.style.color = highlightColor; // Revert to highlight color if checkbox is unchecked
        }
    });
});
