document.addEventListener('DOMContentLoaded', () => {
    // Handle "Pray" button clicks
    const prayButtons = document.querySelectorAll('.pray-button');
    
    prayButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const prayerId = button.getAttribute('data-prayer-id');

            try {
                const response = await fetch(`/pray/${prayerId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    throw new Error('Failed to record prayer');
                }

                const data = await response.json();
                // Update the button text with the new pray count
                button.textContent = `Pray (${data.pray_count})`;
            } catch (error) {
                console.error('Error:', error);
                alert('Something went wrong. Please try again.');
            }
        });
    });

    // Placeholder for future "Save Verse" functionality
    const saveVerseButtons = document.querySelectorAll('.save-verse');
    saveVerseButtons.forEach(button => {
        button.addEventListener('click', () => {
            const verseId = button.getAttribute('data-verse-id');
            console.log(`Save verse with ID: ${verseId} (functionality coming soon)`);
            // Future: Add AJAX call to a save verse endpoint
        });
    });
});
