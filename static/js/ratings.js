document.addEventListener("DOMContentLoaded", () => {
    const reviewForm = document.querySelector("#review-form");

    if (!reviewForm) {
        return;
    }

    const starButtons = document.querySelectorAll(".star-button");
    const ratingInput = document.querySelector("#rating-value");
    const reviewMessage = document.querySelector("#review-message");
    const averageRating = document.querySelector("#average-rating");
    const reviewCount = document.querySelector("#review-count");
    const reviewList = document.querySelector("#review-list");

    function displaySelectedStars(selectedRating) {
        starButtons.forEach((button) => {
            const buttonRating = Number(button.dataset.rating);

            button.classList.toggle(
                "selected",
                buttonRating <= selectedRating,
            );
        });
    }

    function createOrUpdateReview(review) {
        let reviewCard = reviewList.querySelector(
            `[data-review-user-id="${review.user_id}"]`,
        );

        const noReviewsMessage = document.querySelector(
            "#no-reviews-message",
        );

        if (noReviewsMessage) {
            noReviewsMessage.remove();
        }

        if (!reviewCard) {
            reviewCard = document.createElement("article");
            reviewCard.classList.add("review-card");
            reviewCard.dataset.reviewUserId = review.user_id;

            reviewCard.innerHTML = `
                <div class="review-card-heading">
                    <div>
                        <strong class="review-author"></strong>
                        <p class="review-date"></p>
                    </div>
                    <span class="review-stars"></span>
                </div>
                <p class="review-body"></p>
            `;

            reviewList.prepend(reviewCard);
        }

        const author = reviewCard.querySelector(".review-author");
        const date = reviewCard.querySelector(".review-date");
        const stars = reviewCard.querySelector(".review-stars");
        const body = reviewCard.querySelector(".review-body");

        author.textContent = review.username;
        date.textContent = review.updated_at;

        stars.textContent =
            "★".repeat(review.rating)
            + "☆".repeat(5 - review.rating);

        body.textContent = (
            review.review_text
            || "No written review was provided."
        );
    }

    starButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const selectedRating = Number(button.dataset.rating);

            ratingInput.value = selectedRating;
            displaySelectedStars(selectedRating);
            reviewMessage.textContent = "";
        });
    });

    reviewForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!ratingInput.value) {
            reviewMessage.textContent = (
                "Please select a star rating first."
            );

            reviewMessage.classList.add("review-message-error");
            return;
        }

        const submitButton = reviewForm.querySelector(
            'button[type="submit"]',
        );

        submitButton.disabled = true;
        reviewMessage.textContent = "Saving your review...";
        reviewMessage.classList.remove("review-message-error");

        try {
            const response = await fetch(
                reviewForm.action,
                {
                    method: "POST",
                    body: new FormData(reviewForm),
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                    },
                },
            );

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.message
                    || "Your review could not be saved.",
                );
            }

            averageRating.textContent = (
                Number(data.average_rating).toFixed(1)
            );

            reviewCount.textContent = data.review_count;

            createOrUpdateReview(data.review);

            reviewMessage.textContent = data.message;
        } catch (error) {
            reviewMessage.textContent = error.message;
            reviewMessage.classList.add(
                "review-message-error",
            );
        } finally {
            submitButton.disabled = false;
        }
    });
});
