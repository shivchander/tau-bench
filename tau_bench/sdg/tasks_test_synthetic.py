from tau_bench.types import Action, Task

TASKS = [
    Task(
        annotator="1",
        user_id="mohamed_martin_1679",
        instruction="Your user id is mohamed_martin_1679. You need to check your reservation V7NBLQ to confirm the flight details and seating arrangements before your trip.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'V7NBLQ'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="0",
        user_id="harper_ahmed_8302",
        instruction="Your user id is harper_ahmed_8302. You are looking for a flight from JFK to SEA on May 16, 2024; please prioritize direct options.",
        actions=[
            Action(
                name="search_direct_flight",
                kwargs={'origin': 'JFK', 'destination': 'SEA', 'date': '2024-05-16'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="0",
        user_id="daiki_patel_1917",
        instruction="Your user id is daiki_patel_1917. You need to confirm your flight itinerary for reservation 7WKBKD to ensure all details are correct before your upcoming trip.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': '7WKBKD'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="3",
        user_id="liam_garcia_8705",
        instruction="Your user id is liam_garcia_8705. You need to check your reservation 971W9L to confirm your seating preference and baggage allowance before your upcoming trip.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': '971W9L'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="emma_jackson_2190",
        instruction="Your user id is emma_jackson_2190. You want to review your membership benefits and update your contact information.",
        actions=[
            Action(
                name="get_user_details",
                kwargs={'user_id': 'emma_jackson_2190'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="fatima_silva_7735",
        instruction="Your user id is fatima_silva_7735. You want to check your reservation ASFFI5 to confirm the seating arrangement before your upcoming flight.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'ASFFI5'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="mason_johansson_5154",
        instruction="Your user id is mason_johansson_5154. You want to check reservation RB9S17 to confirm the seat assignment and meal preference for your upcoming flight.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'RB9S17'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="raj_garcia_4690",
        instruction="Your user id is raj_garcia_4690. You want to verify the seating arrangements for your reservation 4NQCM5 to ensure your preferences are met.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': '4NQCM5'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="0",
        user_id="juan_lopez_1974",
        instruction="Your user id is juan_lopez_1974. You want to check your reservation YFYFKQ to confirm your seating preferences and meal options before the flight.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'YFYFKQ'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="lei_kim_9517",
        instruction="Your user id is lei_kim_9517. You want to review your membership status and account preferences.",
        actions=[
            Action(
                name="get_user_details",
                kwargs={'user_id': 'lei_kim_9517'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="noah_martin_7498",
        instruction="Your user id is noah_martin_7498. You want to verify the seating arrangements for your reservation 6UJKDA to ensure comfort during your upcoming flight.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': '6UJKDA'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="amelia_li_2415",
        instruction="Your user id is amelia_li_2415. You want to confirm your seat assignment and meal preference for reservation NUCNX0.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'NUCNX0'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="noah_sanchez_4225",
        instruction="Your user id is noah_sanchez_4225. You want to verify the seating arrangements for reservation AQSRNQ to ensure your preferences are met.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'AQSRNQ'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="juan_li_9671",
        instruction="Your user id is juan_li_9671. You are planning a trip for your parents, Daiki and Lei Garcia, to visit Orlando from Charlotte in May. The purpose is a special family event, so you want to ensure everything goes smoothly. Due to their age, you prefer direct flights to minimize travel stress. You need to cancel their existing reservation with id PPHW67 as it no longer fits your plans.\n\nFor the new booking, you want a round trip from Charlotte (CLT) to Orlando (MCO), departing on May 17 and returning on May 19. The flight should be direct and in economy class. You prefer morning flights but are flexible if early afternoon flights significantly reduce costs. Since cost is a consideration, if there are multiple options, choose the one that offers the best value without compromising comfort. Additionally, they should have two pieces of baggage included, but both should be free of charge if possible.\n\nYou plan to use your travel certificate worth $500 for this booking first. If the total cost exceeds $500, use your Visa credit card ending in 8442 to cover the remaining balance. It is crucial for this payment method sequence to minimize out-of-pocket expenses.\n\nFor another existing reservation under Y2DJ0A, you need to upgrade to business class flights on the same dates, May 25, and ensure the itinerary is updated to the new flights HAT270 and HAT064. Use your Visa card for any additional charges incurred due to this change.\n\nMoreover, you want to adjust the baggage allowance for your reservation ID ITSLB7. Increase the total baggage to 4, with 2 of them being non-free. Use your gift card with $120 balance to cover any applicable fees for this baggage update.\n\nReactively engage with the agent to ensure all changes are implemented correctly, and you want the agent to double-check the calculations for payments to avoid any billing errors. You typically refrain from providing personal information unless absolutely necessary, and you rely on the agent to confirm and clarify details as needed.",
        actions=[
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': 'PPHW67'},
            ),
            Action(
                name="search_direct_flight",
                kwargs={'origin': 'CLT', 'destination': 'MCO', 'date': '2024-05-17'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'juan_li_9671', 'origin': 'CLT', 'destination': 'MCO', 'flight_type': 'round_trip', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT064', 'date': '2024-05-17'}, {'flight_number': 'HAT017', 'date': '2024-05-19'}], 'passengers': [{'first_name': 'Daiki', 'last_name': 'Garcia', 'dob': '1973-07-19'}, {'first_name': 'Lei', 'last_name': 'Garcia', 'dob': '1962-08-08'}], 'payment_methods': [{'payment_id': 'certificate_4380964', 'amount': 500}, {'payment_id': 'credit_card_3086580', 'amount': 146}], 'total_baggages': 2, 'nonfree_baggages': 0, 'insurance': 'yes'},
            ),
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'Y2DJ0A', 'cabin': 'business', 'flights': [{'flight_number': 'HAT270', 'date': '2024-05-25'}, {'flight_number': 'HAT064', 'date': '2024-05-25'}], 'payment_id': 'credit_card_3086580'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'ITSLB7', 'total_baggages': 4, 'nonfree_baggages': 2, 'payment_id': 'gift_card_7745140'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="2",
        user_id="anya_anderson_8585",
        instruction="Your user id is anya_anderson_8585. You are planning an important trip and have several specific requirements. Here's what you need to accomplish:\n\nFirstly, you need to update your reservation with ID SAD0VW. You want to change to a cheaper set of economy flights. Your preference is for flights that leave LGA on May 19, 2024, with the flight numbers HAT247 and HAT224, and continuing on May 20, 2024, using flights HAT083 and HAT194. You prefer to use your Mastercard credit card ending in 3219 for payment, but if there's an issue, you can use the one ending in 7702.\n\nAdditionally, for this reservation, you want to include two pieces of luggage. However, you know you have one complimentary baggage allowance with your Gold membership, so you need to pay for only one additional piece. Use your gift card with a balance of $92 for this payment.\n\nNext, you are booking a one-way business class flight from LGA to PHX, departing on May 20, 2024. Prefer flights HAT201 and HAT173. It's crucial to travel on these specific flights due to a conference you must attend. You will take one piece of luggage, and since it's business class, assume one is free, so you’ll pay for one extra if needed. Opt for travel insurance as this trip is critical to your career.\n\nYour payment strategy for this booking involves using the $92 gift card first, to fully deplete it. Then, cover the remaining amount using your Mastercard ending in 3219. Ensure that these payments are prioritized in this specific order to maximize use of the gift card.\n\nYou also need to cancel the reservation with ID ME4T3F. You understand that plans change, and this cancellation is necessary to accommodate your new itinerary. Ensure the refund is processed to your travel certificate if possible.\n\nFinally, you are booking a new reservation for a one-way economy class flight from PHL to EWR on May 20, 2024. Choose flights HAT243 and HAT015, keeping in mind you want to keep costs minimal and have no luggage for this short trip. Use your travel certificate worth $500 for this booking. However, limit the use of the certificate to only what's necessary, as this is a short flight. If additional costs arise, charge them to the remaining balance on your Mastercard ending in 3219.\n\nThroughout these processes, you are proactive in your decisions but rely on the agent to ensure optimal use of your payment resources and to handle any unexpected issues. Consider this trip a top priority and ensure all arrangements align with your preferences and constraints.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'SAD0VW', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT247', 'date': '2024-05-19'}, {'flight_number': 'HAT224', 'date': '2024-05-19'}, {'flight_number': 'HAT083', 'date': '2024-05-20'}, {'flight_number': 'HAT194', 'date': '2024-05-20'}], 'payment_id': 'credit_card_4619444'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'SAD0VW', 'total_baggages': 2, 'nonfree_baggages': 1, 'payment_id': 'gift_card_7656493'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'anya_anderson_8585', 'origin': 'LGA', 'destination': 'PHX', 'flight_type': 'one_way', 'cabin': 'business', 'flights': [{'flight_number': 'HAT201', 'date': '2024-05-20'}, {'flight_number': 'HAT173', 'date': '2024-05-20'}], 'passengers': [{'first_name': 'Anya', 'last_name': 'Anderson', 'dob': '1990-10-15'}], 'payment_methods': [{'payment_id': 'gift_card_4354614', 'amount': 92}, {'payment_id': 'credit_card_6461459', 'amount': 717}], 'total_baggages': 1, 'nonfree_baggages': 1, 'insurance': 'yes'},
            ),
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': 'ME4T3F'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'anya_anderson_8585', 'origin': 'PHL', 'destination': 'EWR', 'flight_type': 'one_way', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT243', 'date': '2024-05-20'}, {'flight_number': 'HAT015', 'date': '2024-05-20'}], 'passengers': [{'first_name': 'Anya', 'last_name': 'Anderson', 'dob': '1990-10-15'}], 'payment_methods': [{'payment_id': 'certificate_3423113', 'amount': 352}], 'total_baggages': 0, 'nonfree_baggages': 0, 'insurance': 'no'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="3",
        user_id="yara_jackson_7992",
        instruction="Your user id is yara_jackson_7992. You need to adjust your travel plans due to a change in your work schedule, which also impacts your vacation plans. Here are your specific requirements:\n\n1. **Cancel an Existing Reservation**: You must cancel your reservation L0UAFK as your schedule no longer allows for that trip. You are proactive in managing your bookings to avoid unnecessary charges.\n\n2. **Flight Search Requirements**:\n   - You are looking for a new flight from DTW (Detroit Metropolitan Airport) to LGA (LaGuardia Airport) on May 18, 2024. You prefer flights that have at most one stopover since you want a balance between cost and convenience.\n   - Simultaneously, explore direct flights from PHX (Phoenix Sky Harbor) to LGA on the same date, as your plans may require you to depart from Phoenix instead. Your choice will depend on the best balance between price and travel time.\n\n3. **Booking Preferences**:\n   - Once the search is done, book a one-way flight from PHX to LGA in economy class for May 18, choosing flight number HAT066.\n   - You are conscious of budget constraints; therefore, use your gift card first, which has a balance of $87. Cover any remaining balance using your Mastercard credit card ending in 3505.\n   - You are carrying 1 piece of baggage but do not require additional purchase for non-free baggage, and you decline travel insurance to keep costs low.\n\n4. **Modify an Existing Reservation**:\n   - You need to update your reservation 09F9WJ to include 1 non-free checked baggage. Use your Mastercard credit card ending in 3505 for any additional baggage fees.\n\n5. **Decision Criteria**:\n   - If the PHX to LGA flight is too expensive or inconvenient, fall back on the DTW to LGA one-stop option. You prioritize the cheapest available flight that meets your criteria.\n   - If neither option is viable, consider rescheduling your trip, but prefer not to change the May 18th travel date if possible.\n   \n6. **Behavioral Instructions**:\n   - You are reactive in your interactions with the airline agent and prefer not to provide redundant information unless necessary.\n   - You trust the agent to calculate and decide on the most cost-effective payment method based on your available options.\n\nThis situation is urgent as your travel dates are approaching, and any delays in updating your reservations could lead to inconvenience. Implement these changes to align your travel plans with your current commitments effectively.",
        actions=[
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': 'L0UAFK'},
            ),
            Action(
                name="search_onestop_flight",
                kwargs={'origin': 'DTW', 'destination': 'LGA', 'date': '2024-05-18'},
            ),
            Action(
                name="search_direct_flight",
                kwargs={'origin': 'PHX', 'destination': 'LGA', 'date': '2024-05-18'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'yara_jackson_7992', 'origin': 'PHX', 'destination': 'LGA', 'flight_type': 'one_way', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT066', 'date': '2024-05-18'}], 'passengers': [{'first_name': 'Yara', 'last_name': 'Jackson', 'dob': '1989-01-08'}], 'payment_methods': [{'payment_id': 'gift_card_6955135', 'amount': 87}, {'payment_id': 'credit_card_6633575', 'amount': 77}], 'total_baggages': 1, 'nonfree_baggages': 0, 'insurance': 'no'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': '09F9WJ', 'total_baggages': 1, 'nonfree_baggages': 1, 'payment_id': 'credit_card_6633575'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="2",
        user_id="mason_garcia_8795",
        instruction="Your user id is mason_garcia_8795. You are planning a trip and have a few changes and new bookings to make. Here’s what you need:\n\n1. **Current Reservation Update**: You have an upcoming trip and need to check some details. Specifically, you want to view the reservation details for reservation ID ZKBXFF as you need to verify the flight times and details before making any changes.\n\n2. **Baggage Adjustment**: Once you have confirmed the details of reservation ZKBXFF, you decide to add an additional checked bag to this reservation. You have a total of 2 bags now, but only 1 of these is chargeable. You want to use your gift card to pay for any additional charges, prioritizing the gift card with a balance of $229 (gift_card_2929673).\n\n3. **Reservation Cancellation**: You realize that you will not be able to make another trip for which you have a reservation ID VYVD4J. You want to cancel this reservation. You are not concerned about any refund at this point, but you prefer canceling it now rather than risking a no-show. \n\n4. **New Flight Search**: You need to book a new flight from Phoenix (PHX) to San Francisco (SFO) on May 18, 2024. You prefer a one-stop flight as long as the total travel time is not excessively long. Your priority is to fly at a time that allows you to arrive in San Francisco no later than 5 PM due to an important event you need to attend that evening.\n\n5. **Booking New Reservation**: Once you find suitable flights, you want to book a round-trip in economy class, returning on May 29, 2024. You are flexible with the return time, but prefer afternoon departures if available. You decide to book using your travel certificate worth $500 (certificate_2511595), but you only plan to use $349 of it, since it covers the cost of the trip. You do not require any travel insurance for this flight. For baggage, you decide to travel light with just one carry-on and no checked bags.\n\nIn all these actions, you prefer to be reactive to the agent’s prompts and will not volunteer additional information unless specifically asked. You trust the agent to help you with calculations and decisions, especially concerning payment options and baggage charges.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'ZKBXFF'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'ZKBXFF', 'total_baggages': 2, 'nonfree_baggages': 1, 'payment_id': 'gift_card_2929673'},
            ),
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': 'VYVD4J'},
            ),
            Action(
                name="search_onestop_flight",
                kwargs={'origin': 'PHX', 'destination': 'SFO', 'date': '2024-05-18'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'mason_garcia_8795', 'origin': 'PHX', 'destination': 'SFO', 'flight_type': 'round_trip', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT032', 'date': '2024-05-18'}, {'flight_number': 'HAT123', 'date': '2024-05-29'}], 'passengers': [{'first_name': 'Mason', 'last_name': 'Garcia', 'dob': '1988-03-15'}], 'payment_methods': [{'payment_id': 'certificate_2511595', 'amount': 349}], 'total_baggages': 1, 'nonfree_baggages': 0, 'insurance': 'no'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="ivan_garcia_1794",
        instruction="Your user id is ivan_garcia_1794. You have an existing reservation (LV5MG2) that you want to update to include a more comfortable experience by upgrading to business class. You prefer to fly with flight numbers HAT115 and HAT129 on May 20, 2024, and you are willing to use your Visa credit card ending in 8790 for the payment. \n\nHowever, you also have another reservation (PG7O11) that conflicts with your updated travel plans, so you need to cancel it to avoid any overlaps. \n\nAdditionally, you need to add one checked bag to your updated reservation LV5MG2. Since you prefer to manage expenses efficiently, you would like to use your Visa credit card ending in 8149 for the baggage fees.\n\nFor a new booking, you're planning a family trip for yourself, Ivan Garcia, along with Omar Santos and Maria Garcia from Philadelphia (PHL) to LaGuardia (LGA) with round-trip flights. You want to depart on May 18, 2024, with flight HAT296 and return on May 19, 2024, with flight HAT172. You prefer business class for comfort and are interested in purchasing travel insurance for this trip. While there are two adults and one child in your party, you want to stay within a budget limit and would like the agent to calculate the total cost of $378 and $337, plus a $30 service fee for the insurance.\n\nYou plan to use your Visa credit card ending in 8790 to pay for this booking and will allocate a total of $1,725 for this trip. Ensure no additional baggage fees are incurred by keeping your baggage count within the allowable limit. \n\nYou are proactive in managing your travel plans and prefer not to repeat information that can be found in your user profile, such as your date of birth. You appreciate the agent handling all calculations and logistics for you, especially since you are not inclined to perform any manual math. Your travel is urgent due to a family commitment, and you prefer a smooth process, minimizing hassles at each stage. If any changes are required, you're open to alternative options as long as they stay within your stated constraints.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'LV5MG2', 'cabin': 'business', 'flights': [{'flight_number': 'HAT115', 'date': '2024-05-20'}, {'flight_number': 'HAT129', 'date': '2024-05-20'}], 'payment_id': 'credit_card_8638712'},
            ),
            Action(
                name="calculate",
                kwargs={'expression': '378 + 337 + 30'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'LV5MG2', 'total_baggages': 1, 'nonfree_baggages': 1, 'payment_id': 'credit_card_7155120'},
            ),
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': 'PG7O11'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'ivan_garcia_1794', 'origin': 'PHL', 'destination': 'LGA', 'flight_type': 'round_trip', 'cabin': 'business', 'flights': [{'flight_number': 'HAT296', 'date': '2024-05-18'}, {'flight_number': 'HAT172', 'date': '2024-05-19'}], 'passengers': [{'first_name': 'Omar', 'last_name': 'Santos', 'dob': '1969-09-19'}, {'first_name': 'Ivan', 'last_name': 'Garcia', 'dob': '1980-02-29'}, {'first_name': 'Maria', 'last_name': 'Garcia', 'dob': '1982-01-15'}], 'payment_methods': [{'payment_id': 'credit_card_8638712', 'amount': 1725}], 'total_baggages': 2, 'nonfree_baggages': 0, 'insurance': 'yes'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="0",
        user_id="yara_rossi_1806",
        instruction="Your user id is yara_rossi_1806. You recently received news that your cousin's wedding in Paris has been rescheduled to May 17, 2024, and you need to adjust your travel plans accordingly. You are proactive and prefer handling the details yourself but are open to assistance if needed.\n\nYou have a Gold Membership with our airline, which allows you certain privileges, such as priority boarding and additional baggage allowance, which you want to make the most of during this trip. You are currently holding a reservation with the ID LQZT3N that you initially planned for a different date. Now, you want to update this reservation to reflect your new travel plans.\n\n1. **Flight Preferences**:\n    - **Travel Date**: May 17, 2024\n    - **Flight Number**: You specifically want flight HAT295 as it aligns perfectly with your schedule and offers the best balance of price and convenience.\n    - **Cabin Class**: You prefer to fly in economy to save on costs, even though you have access to premium cabins due to your membership.\n    - **Time Preferences**: You prefer flights in the afternoon or evening, as this allows you to attend a morning event at home before you depart.\n\n2. **Payment Strategy**:\n    - You prefer to use your Visa credit card ending in 3926 (payment ID: credit_card_6432530) for any additional charges that arise from this change. This card is currently set as your default payment method.\n    - You are budget-conscious and want to ensure there are no unnecessary charges, but you understand a small change fee may be necessary.\n\n3. **Baggage Allowance**:\n    - For a separate reservation (EEK48Y), you currently have 2 pieces of baggage. You realize you will need to bring an additional piece due to gifts for the wedding and need to update this to a total of 3 baggages.\n    - You want to ensure that all your baggage fits within the free allowance included with your Gold Membership, so no additional payment is needed for this reservation's baggage update.\n\n4. **Conditional Decision Making**:\n    - If flight HAT295 is unavailable for the updated date, you would like to be placed on the next available economy flight on the same day, preferably after 3 PM.\n    - If this option can't be used, you are open to flying the evening before but require assurance of minimal layover time, prioritizing a direct flight if possible.\n  \nYou do not prefer to provide additional personal information over the phone unless absolutely necessary, as you are cautious about privacy. You typically handle these changes through the airline's app or website and prefer a confirmation email as a follow-up. You want this handled promptly as there is a sense of urgency due to upcoming commitments.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'LQZT3N', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT295', 'date': '2024-05-17'}], 'payment_id': 'credit_card_6432530'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'EEK48Y', 'total_baggages': 3, 'nonfree_baggages': 0, 'payment_id': 'credit_card_6432530'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="2",
        user_id="harper_davis_5069",
        instruction="Your user id is harper_davis_5069. You are planning a significant trip and have two existing reservations, but need to make some adjustments to ensure everything aligns with your schedule and budget preferences.\n\nFirstly, for your reservation ID WLXS0L, you realized that you'll have one checked bag, which needs to be added to your reservation. You are keen on using your gift cards to cover any additional fees. You prefer to use the gift card with the largest balance ($282) to pay for this service, as it should cover the cost entirely. Ensure to instruct the agent to update your reservation with one non-free baggage and use the gift card ending in 7215260 for the payment.\n\nFor your second reservation, W0I4AJ, you need to reschedule your flight as your travel plans have changed. Your new flight should be on May 16, 2024. You prefer to stay within economy class to manage costs. You are looking for a flight on this specific day and flight number HAT184 fits your schedule perfectly. Make sure to use your Mastercard credit card ending in 5038 for any additional charges related to this update, as it is your preferred method for handling such modifications.\n\nYou have set clear time constraints for both updates: you are available in the mornings but not before 9 am, so ensure any discussions or confirmations can be addressed during this timeframe. \n\nYour travel plans are motivated by a family reunion you must attend, which adds urgency to these changes. You prefer not to deal with complicated calculations or estimations, so rely on the agent to handle any necessary computations or adjustments in fees.\n\nYou are generally proactive when it comes to planning, so you should specify that you will provide any additional information promptly when asked by the agent, but you do not prefer to confirm details that are already within your user profile, like your birthday.\n\nOverall, your strategy emphasizes using available gift cards first to minimize out-of-pocket expenses and ensuring that all reservations align with your preferred schedule and flight class selections.",
        actions=[
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'WLXS0L', 'total_baggages': 1, 'nonfree_baggages': 1, 'payment_id': 'gift_card_7215260'},
            ),
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'W0I4AJ', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT184', 'date': '2024-05-16'}], 'payment_id': 'credit_card_7396423'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="3",
        user_id="mei_patel_4436",
        instruction="Your user id is mei_patel_4436. You are planning an important trip with your reservation ID E17VRA and need to modify it for a crucial family event. You want to update the flights to economy class, and the new itinerary should include two specific flights. The first flight should be HAT114 on May 19, 2024, followed by a connecting flight, HAT156, on May 20, 2024. You are particular about these dates as they align perfectly with your event schedule.\n\nIn terms of timing and convenience, you have a preference for flights that do not depart before 9 AM to allow for a relaxed morning, yet they should not stretch too late into the evening, ensuring a comfortable arrival. You prefer flights with the least stopover time to maximize your efficiency and reduce travel fatigue.\n\nRegarding payment, you are conscious about how the costs align with your resources. You should prioritize using your Mastercard credit card ending in 1562 for the flight updates, as it offers you travel cashback benefits. However, if the charges exceed your expected threshold for this card, which is primarily budgeted at $600, you would then use your Mastercard credit card ending in 4094.\n\nAdditionally, you need to update your baggage allowance to include three checked bags since you’ll be carrying items for family members. It’s important to be mindful of your baggage payment strategy. You should use your Mastercard credit card ending in 4094 for this purpose, as it provides additional baggage insurance.\n\nYour behavior is proactive when providing necessary information but prefers not to disclose details outside what is needed. You want the agent to ensure all changes are confirmed without any errors, as any mistake could disrupt your family plans. You value the agent’s assistance in verifying that all updates adhere to your preferences and time constraints.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'E17VRA', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT114', 'date': '2024-05-19'}, {'flight_number': 'HAT156', 'date': '2024-05-20'}], 'payment_id': 'credit_card_2126547'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'E17VRA', 'total_baggages': 3, 'nonfree_baggages': 3, 'payment_id': 'credit_card_4435842'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="3",
        user_id="amelia_rossi_1651",
        instruction="Your user id is amelia_rossi_1651. You are planning a trip under reservation MZLGZ8 for a special family reunion, so it's important that everything is confirmed and smooth. You need to update your flight details and baggage preferences accordingly.\n\nFirstly, you want to add two checked bags to your reservation. Since you are traveling with gifts and personal items, you will need both bags, which are not included in your current booking. You prefer to use your Mastercard credit card ending in 7564 for any additional charges.\n\nRegarding your flights, you want to ensure that you are flying in economy class for all segments of this trip. Your preferred flights are HAT023, HAT082 on May 19, 2024, and HAT085 on May 20, 2024. It is crucial for you to maintain these flights because they align with events scheduled around your reunion. If for any reason these flights are unavailable, you would like the agent to find the next best alternative within the same class and dates.\n\nYou are proactive and open to discussing changes but will not provide details like your birthday again since it's already in your user profile. You prefer fast, direct communication and want the agent to handle all calculations regarding costs and payments.\n\nFor payment, use your Mastercard ending in 7564 for any additional fees associated with these changes. This is your preferred method, and you rely on it for its reliability and efficiency. Should there be any issue with this card, you prefer to be contacted immediately.\n\nThis trip is not only time-sensitive but also emotionally significant, so you need everything to be confirmed promptly and accurately.",
        actions=[
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'MZLGZ8', 'total_baggages': 2, 'nonfree_baggages': 2, 'payment_id': 'credit_card_4240750'},
            ),
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'MZLGZ8', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT023', 'date': '2024-05-19'}, {'flight_number': 'HAT082', 'date': '2024-05-19'}, {'flight_number': 'HAT085', 'date': '2024-05-20'}], 'payment_id': 'credit_card_4240750'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="noah_silva_2256",
        instruction="Your user id is noah_silva_2256. You have a reservation for an upcoming trip with the reservation ID T8QHPY and wish to update your travel details. You want to change your flights to fly on May 19, 2024, for both outbound and return flights. You prefer to travel in business class as it accommodates your need for comfort during travel due to recent work commitments that have left you quite tired.\n\nYou wish to fly on the fastest available flights, ideally direct, but you are willing to accept a one-stop flight if it significantly reduces travel time. Your departure should not be before 9am, as you need some time in the morning to handle work-related tasks. You prefer evening returns if possible, to maximize your time at your destination for business meetings.\n\nYour priority is to use your Mastercard credit card ending in 9170 for the fare adjustments. If there's an issue with this card, you prefer to be notified so you can decide on an alternative payment method. For baggage, you wish to bring one additional checked bag and pay for it using your gift card with $112 balance, as you aim to optimize your available funds.\n\nYou are reactive and prefer concise communication, focusing only on necessary details. You require the agent to confirm each change so you can ensure no details are overlooked. If there are additional costs beyond your budget, you would like to be informed before any charges are incurred, as you need to stay within your travel expense allocation for this trip.\n\nThis update is of moderate urgency; while not immediate, you wish to have it resolved within this week to avoid potential fare increases. You do not prefer to provide any additional personal details outside of your user id, as your preferences and payment methods are already on file.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'T8QHPY', 'cabin': 'business', 'flights': [{'flight_number': 'HAT173', 'date': '2024-05-19'}, {'flight_number': 'HAT047', 'date': '2024-05-19'}], 'payment_id': 'credit_card_7773542'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'T8QHPY', 'total_baggages': 1, 'nonfree_baggages': 1, 'payment_id': 'gift_card_9130446'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="2",
        user_id="ethan_hernandez_6400",
        instruction="Your user id is ethan_hernandez_6400. You need to modify two of your existing reservations due to a change in your travel plans, and you'd like assistance to ensure everything is set correctly.\n\nFirstly, for your reservation 7HXRPX, you initially planned to travel light, but circumstances have changed, and you now need to bring along additional baggage. You want to add two total pieces of baggage to this reservation. However, you are aware that only one additional baggage comes free with your silver membership, so you need to purchase the second one. You prefer to use your Visa credit card ending in 1332, which you have previously saved in your profile as credit_card_9038105, to cover any additional baggage fees.\n\nNext, for your trip under reservation 4069WE, you've decided to adjust your flight details for maximum comfort during your journey. You prefer to fly in economy class for this reservation. You have specific flights in mind for this journey: flight HAT083 on May 19, 2024, and the connecting flight HAT194 on the same date. You want to ensure you stay within your budget, so you would like to confirm that these flights are available at reasonable rates. Again, your preferred mode of payment is your Visa credit card ending in 1332 (credit_card_9038105), as you find it convenient and secure.\n\nYou prefer not to fly before noon, as you enjoy a leisurely morning without the rush, and you do not have any specific geographic constraints regarding airports, as long as they are within the original route. You are proactive and would like the agent to confirm all charges and details before finalizing the changes, ensuring no unexpected costs arise later. You prefer not to provide any additional personal information during the interaction unless absolutely necessary, as your profile should already contain the required details.\n\nYour motivation for these changes stems from a combination of personal commitments and maximizing the efficiency and comfort of your travel experience. Your attention to detail and preference for clarity in financial transactions is critical, and you trust the agent to provide you with comprehensive support in this process.",
        actions=[
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': '7HXRPX', 'total_baggages': 2, 'nonfree_baggages': 1, 'payment_id': 'credit_card_9038105'},
            ),
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': '4069WE', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT083', 'date': '2024-05-19'}, {'flight_number': 'HAT194', 'date': '2024-05-19'}], 'payment_id': 'credit_card_9038105'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="chen_rossi_8135",
        instruction="Your user id is chen_rossi_8135. You are planning a business trip and need to make specific travel arrangements. Here's what you need to do:\n\n1. **Cancel an Existing Reservation**: Due to a change in schedule, you need to cancel an existing reservation with the id UGHGGR. Once this is done, proceed with the new booking.\n\n2. **Book a New Reservation**: You need to fly from Phoenix (PHX) to Orlando (MCO) for a round-trip business meeting. You prefer to travel in business class for added comfort. Here are the specifics:\n   - **Outbound Flight**: You choose flight HAT181 departing on May 19, 2024. \n   - **Return Flight**: You will take flight HAT161 on May 20, 2024.\n\n3. **Passenger Details**: Ensure the booking is under your name, Chen Rossi, with the date of birth listed as August 13, 1985. \n\n4. **Baggage**: You will be traveling light, so you'll only have one piece of luggage that falls under the free baggage allowance. No additional baggage will be required for this trip.\n\n5. **Payment Strategy**: \n   - First, apply your travel certificate worth $100 (certificate_9001327) to the total cost.\n   - The remaining balance should be covered using your Mastercard credit card ending in 1609. Be sure to use this specific card to finalize the transaction.\n\n6. **Insurance**: You do not require flight insurance for this trip, so make sure not to include it in your booking.\n\n7. **Behavioral Instructions**: You prefer to be proactive in gathering information and making decisions but do not want to disclose personal details beyond what is necessary for booking. If there are any financial calculations needed, you prefer that the agent handles them for you.\n\n8. **Motivation & Constraints**: The urgency of this booking is due to an important business meeting that requires your in-person attendance. You have a preference for flying at convenient times, so please ensure the flights align with typical business hours. If the preferred flights are unavailable, choose the next best option within business class on the same dates.\n\n9. **Conditional Decision Logic**: If your preferred flights are not available due to scheduling or capacity, opt for the next best available business class flights that depart no earlier than 9 AM and return no later than 7 PM. If even this is not feasible, consider adjusting the dates to the nearest available options, while keeping the overall trip as short as possible.\n\nBy following these detailed instructions, you will ensure that your upcoming travel plans are adjusted to meet your needs while optimizing your existing resources and membership benefits.",
        actions=[
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': 'UGHGGR'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'chen_rossi_8135', 'origin': 'PHX', 'destination': 'MCO', 'flight_type': 'round_trip', 'cabin': 'business', 'flights': [{'flight_number': 'HAT181', 'date': '2024-05-19'}, {'flight_number': 'HAT161', 'date': '2024-05-20'}], 'passengers': [{'first_name': 'Chen', 'last_name': 'Rossi', 'dob': '1985-08-13'}], 'payment_methods': [{'payment_id': 'certificate_9001327', 'amount': 100}, {'payment_id': 'credit_card_8191674', 'amount': 721}], 'total_baggages': 1, 'nonfree_baggages': 0, 'insurance': 'no'},
            ),
        ],
        outputs=['sample_output'],
    ),
    Task(
        annotator="1",
        user_id="aarav_brown_5556",
        instruction="Your user id is aarav_brown_5556. You have a few specific modifications to make for your upcoming travel plans. This is an urgent request as you have just realized some changes need to be made before your trip.\n\n1. **Baggage Update for Existing Reservation:**\n   - You need to update the baggage count for your reservation with id 269EJV. Originally, you did not have any additional baggage, but now you need to add one non-free checked bag.\n   - You want to use one of your gift cards for this transaction. Specifically, use the gift card with the balance of $299. If the cost exceeds this gift card, you prefer not to proceed with adding the baggage on this reservation yet.\n   - You are reactive and prefer concise communication; respond only with essential information when prompted by the customer service agent.\n\n2. **Flight Changes for Existing Reservation:**\n   - You have a reservation with id 6BL29B, and you need to adjust the flights within this reservation.\n   - The earlier specified flights do not meet your schedule, and you must ensure that you depart and return between May 18th and May 20th.\n   - Your preference is to fly with the following sequence and dates:\n      - Depart on flight HAT281 on May 18, 2024\n      - Followed by flights HAT003, HAT046, and HAT282, all on May 20, 2024\n   - You prefer economy class for cost-effectiveness, even though you understand this might mean fewer amenities.\n   - For this flight adjustment, you intend to use your Visa credit card ending in 2581. If it's not possible to use this card due to credit limits or other issues, do not make these flight changes and instead look for flights on alternative dates.\n   - You prefer direct flights, but are open to stopovers if they significantly reduce the cost. If the total cost exceeds your budget, only proceed if no other cheaper options are available.\n   - You're proactive in ensuring that there are no additional fees beyond what you've agreed upon for the credit card payment, so confirm all costs with the agent before finalizing.\n\n3. **General Preferences and Constraints:**\n   - You don’t prefer flights that depart before 9 am to allow for a comfortable morning routine.\n   - If the discussed changes cannot be made within your budget constraints, request that the agent provides alternate flights or options that are more budget-friendly.\n   - In all communications, you prefer to keep your personal information minimal, relying on what's already in your user profile.\n\nYou are focused on ensuring these changes are budget-friendly and meet your schedule, as the trip is crucial for both personal and professional reasons. The urgency stems from needing everything settled promptly to avoid disruptions in your plans.",
        actions=[
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': '269EJV', 'total_baggages': 1, 'nonfree_baggages': 1, 'payment_id': 'gift_card_9998687'},
            ),
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': '6BL29B', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT281', 'date': '2024-05-18'}, {'flight_number': 'HAT003', 'date': '2024-05-20'}, {'flight_number': 'HAT046', 'date': '2024-05-20'}, {'flight_number': 'HAT282', 'date': '2024-05-20'}], 'payment_id': 'credit_card_3029145'},
            ),
        ],
        outputs=['327', '1000', '1786'],
    ),
    Task(
        annotator="1",
        user_id="olivia_jackson_7257",
        instruction="Your user ID is olivia_jackson_7257. You want to update your upcoming trip to include additional baggage and book a new one-way flight from Detroit (DTW) to Phoenix (PHX) on May 20, 2024. Here are the details and preferences for both actions:\n\n### Updating Existing Reservation:\n1. **Reservation ID**: You need to update reservation ID 9YE5D6.\n2. **Baggage Details**: You currently have 1 baggage included, but you want to add an extra checked bag, making it 2 in total, with 1 being non-free.\n3. **Payment Preference**: You prefer using your Visa credit card ending in 3838 for this transaction. Ensure it is charged appropriately.\n\n### New Flight Booking:\n1. **Travel Dates & Preferences**:\n   - You want to fly on May 20, 2024, and prefer a morning departure, ideally no earlier than 8 AM to maximize your time in Phoenix.\n   - You are flexible with a direct flight, but if a stopover significantly reduces cost, you’re open to it.\n   \n2. **Flight Details**:\n   - You have already chosen flight HAT035, which suits your time preferences.\n   - Cabin class is economy, as budget efficiency is a priority for this trip.\n\n3. **Personal Info**:\n   - Your full name is Olivia Jackson, and your date of birth is April 19, 1983.\n\n4. **Payment Strategy**:\n   - You have a total budget of $175 for this booking. First, use any available travel credits, then proceed with your Visa credit card ending in 3838 for the remaining balance, ensuring the total charge does not exceed your budget.\n\n5. **Baggage & Insurance**:\n   - No additional baggage is needed for this trip, and you opt out of travel insurance based on your assessment that it is not necessary.\n\n6. **Behavioral Instructions**:\n   - You are proactive, providing necessary details upfront and asking follow-up questions as needed.\n   - You prefer not to provide additional personal information unless required for the booking process.\n\n7. **Motivations & Urgency**:\n   - This trip is for a personal family engagement in Phoenix, making timely updates and bookings a priority. You need everything confirmed at the earliest to avoid last-minute hassles.\n\n8. **Conditional Logic**:\n   - If the selected flight HAT035 is not available or exceeds the budget, choose the next best option within your budget and time preference. If none exist, consider flights with a stopover that meet the budget requirement.\n\nBy following these detailed preferences, you aim to efficiently manage your travel plans without exceeding your financial limits or compromising on your schedule.",
        actions=[
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': '9YE5D6', 'total_baggages': 2, 'nonfree_baggages': 1, 'payment_id': 'credit_card_2480682'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'olivia_jackson_7257', 'origin': 'DTW', 'destination': 'PHX', 'flight_type': 'one_way', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT035', 'date': '2024-05-20'}], 'passengers': [{'first_name': 'Olivia', 'last_name': 'Jackson', 'dob': '1983-04-19'}], 'payment_methods': [{'payment_id': 'credit_card_2480682', 'amount': 174}], 'total_baggages': 0, 'nonfree_baggages': 0, 'insurance': 'no'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="0",
        user_id="noah_lopez_2532",
        instruction="Your user id is noah_lopez_2532. For your current reservation to Los Angeles (reservation id: E9E7HC), you wish to update your flight details to align with a new itinerary. Your priority is to switch the cabin class to economy for all flights and ensure the following flight schedule: a departure on May 17 with flights HAT077 and HAT233, and a return on May 20 with flights HAT060 and HAT288. You understand there might be price differences with this change and prefer to use your Visa credit card ending in 5999 for any additional costs. You need two pieces of baggage, one of which will not be complimentary, so please charge the associated fees to the same Visa card.\n\nAdditionally, you are planning a new one-way reservation for a business trip from New York's LaGuardia (LGA) to Phoenix (PHX) on May 19. You prefer a late morning or early afternoon departure. The flight should be in business class for a comfortable travel experience given the work commitments in Phoenix. You will be traveling with Evelyn Lee, born on April 4, 1950, and you need to book a ticket for her as well. Baggage arrangements should allow for one checked bag, understanding that one will incur an additional cost.\n\nTo manage expenses effectively, please use your travel certificate worth $500. Prioritize using the travel certificate for this new booking, aiming to cover as much of the cost as possible. Allocate $349 of the certificate for this booking. If the certificate doesn't cover all costs, proceed with the Visa credit card ending in 5999 for any remaining balance. Additionally, you want insurance for this trip, anticipating any unforeseen events.\n\nYou are in a proactive mindset for these arrangements, so be prepared to make real-time decisions if necessary. However, you do not wish to manually calculate costs or consider alternative payment methods beyond the specified ones, so rely on the agent to ensure everything fits within your set parameters. The update to your existing reservation and the new booking are both urgent as they relate to a critical business engagement in Phoenix.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'E9E7HC', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT077', 'date': '2024-05-17'}, {'flight_number': 'HAT233', 'date': '2024-05-17'}, {'flight_number': 'HAT060', 'date': '2024-05-20'}, {'flight_number': 'HAT288', 'date': '2024-05-20'}], 'payment_id': 'credit_card_3623927'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'E9E7HC', 'total_baggages': 2, 'nonfree_baggages': 1, 'payment_id': 'credit_card_3623927'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'noah_lopez_2532', 'origin': 'LGA', 'destination': 'PHX', 'flight_type': 'one_way', 'cabin': 'business', 'flights': [{'flight_number': 'HAT150', 'date': '2024-05-19'}], 'passengers': [{'first_name': 'Evelyn', 'last_name': 'Lee', 'dob': '1950-04-04'}], 'payment_methods': [{'payment_id': 'certificate_5542518', 'amount': 349}], 'total_baggages': 1, 'nonfree_baggages': 1, 'insurance': 'yes'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="olivia_rossi_1087",
        instruction="Your user id is olivia_rossi_1087. You recently realized that the trip you had planned (reservation ID 4FORX8) is no longer feasible due to a sudden work commitment, so you need to cancel it. However, you must attend a meeting in Houston on May 18, and therefore you need to book a round-trip flight from Denver to Houston. You prefer to fly economy and wish to depart on May 18 as early as possible, ideally on a direct flight. You plan to return the next day, May 19, and prefer a flight leaving Houston in the late afternoon or early evening to maximize your time there without having to rush. \n\nWhen deciding on this new reservation, you have a travel certificate worth $150 that you want to use first. To cover any remaining balance, you prefer to use your Mastercard credit card ending in 6883. Your budget for this trip is capped at $300; if the total exceeds this, you will reconsider your trip dates or times. Your silver membership might offer you some benefits, so ask about any available discounts or promotions. \n\nYou will be traveling with one bag, and you are aware that your membership allows for some baggage allowances. You do not require travel insurance for this trip, as your credit card provides sufficient coverage. \n\nAdditionally, you have an upcoming trip with reservation ID 5JATGA. You realized that you will need to bring an extra piece of baggage for this journey. You want to update this reservation to include two bags, with one being non-free. Use your credit card ending in 6883 to cover any additional baggage fees. \n\nFor all your interactions, be proactive in ensuring that any changes are confirmed with detailed receipts and confirmations sent to your email. You are reactive during this process and will provide additional details only if requested by the agent. Your main motivation is to balance work commitments with cost-efficiency and time management, ensuring you don't overspend while meeting all your travel needs.",
        actions=[
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': '4FORX8'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'olivia_rossi_1087', 'origin': 'DEN', 'destination': 'IAH', 'flight_type': 'round_trip', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT229', 'date': '2024-05-18'}, {'flight_number': 'HAT175', 'date': '2024-05-19'}], 'passengers': [{'first_name': 'Olivia', 'last_name': 'Rossi', 'dob': '1996-08-26'}], 'payment_methods': [{'payment_id': 'certificate_9153684', 'amount': 150}, {'payment_id': 'credit_card_8752089', 'amount': 130}], 'total_baggages': 1, 'nonfree_baggages': 0, 'insurance': 'no'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': '5JATGA', 'total_baggages': 2, 'nonfree_baggages': 1, 'payment_id': 'credit_card_8752089'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="2",
        user_id="raj_ito_8898",
        instruction="Your user id is raj_ito_8898. You are planning a family trip and need to make some changes and additions to your current reservations. You like to be cost-efficient and prefer economy flights unless there's a significant time-saving with an upgrade. \n\nFirstly, you're planning to update your reservation (ID: ZWI06B) for an upcoming trip. You want to switch to economy class for both legs of the journey. Make sure both flights are with flight numbers HAT098 on May 21 and HAT298 on May 29. You have a preference for flights that depart between 10 AM and 2 PM local time, as you want to avoid early morning and late evening travel. You plan to use your Visa credit card ending in 7324 for this transaction.\n\nFor another reservation (ID: JNV20G), you need to adjust the baggage arrangements. You’ll be traveling with two bags, of which one is extra and will require payment. Aim to balance your luggage allocation efficiently, and use your Mastercard ending in 9546 to cover any additional fees.\n\nAdditionally, you intend to book a new reservation for a one-way flight from Detroit (DTW) to Phoenix (PHX) scheduled for May 18, 2024. This booking is for your mother, Isabella Johansson, ensuring she travels comfortably in economy class. Isabella prefers flights that allow her to arrive by early afternoon. You have a budget for this flight, preferring the most cost-effective option available. For payment, primarily use your Visa credit card ending in 7324, but ensure the total cost does not exceed $200. If the flight costs more, consider splitting the payment between your Visa and Mastercard, with Visa covering the initial $195. No additional baggage or travel insurance is needed for this booking.\n\nIn approaching these tasks, you are proactive in gathering information but prefer the agent to confirm details. If any of your primary options are unavailable, you'd appreciate recommendations for alternatives that closely match your preferences. Your priority is ensuring timely and economical travel arrangements, as this trip holds personal significance for family reunions.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'ZWI06B', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT098', 'date': '2024-05-21'}, {'flight_number': 'HAT298', 'date': '2024-05-29'}], 'payment_id': 'credit_card_8368961'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'JNV20G', 'total_baggages': 2, 'nonfree_baggages': 1, 'payment_id': 'credit_card_7614961'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'raj_ito_8898', 'origin': 'DTW', 'destination': 'PHX', 'flight_type': 'one_way', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT275', 'date': '2024-05-18'}], 'passengers': [{'first_name': 'Isabella', 'last_name': 'Johansson', 'dob': '1960-08-21'}], 'payment_methods': [{'payment_id': 'credit_card_8368961', 'amount': 195}], 'total_baggages': 0, 'nonfree_baggages': 0, 'insurance': 'no'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="0",
        user_id="mei_ito_6207",
        instruction="Your user id is mei_ito_6207. You've recently been promoted at work, and as a reward, your company is sending you on a business trip to attend a crucial conference in Sydney. You’re keen to make the most of this opportunity not only professionally but also personally by ensuring comfort during your travel.\n\nFor your upcoming trip with reservation ID Q8YZY1, you would like to upgrade your flights to business class to enhance your travel experience. Your conference begins on May 18, so you need to arrive by the evening of May 17. You prefer to depart on May 16, and your flights are with HAT Airlines. You want to make sure you’re on flight number HAT133 on May 16 and flight number HAT220 on May 17. \n\nYou have a strict requirement that your outbound flight does not depart before 9 AM to allow you time to finalize work at your office the morning of departure. Price is not a primary concern for the upgrade, but you do want to use your Mastercard credit card ending in 4474 for payment unless there's an issue with it—in that case, use your other card ending in 1276. \n\nMoreover, you’ll be bringing two bags with you. Although your membership allows one free baggage, you will need to pay for the additional checked bag. You prefer to use your Mastercard ending in 1276 for this payment to keep personal and business expenses separate. \n\nSeparately, you have another reservation ID I9GT07 that you made in error as it conflicts with your business trip. Since this trip is no longer needed, you want to cancel it entirely and ensure any potential refund is processed back to the original payment method used. \n\nYou are proactive in managing your reservations and prefer to handle changes promptly to avoid last-minute issues. You are also conscious of maintaining a clear record of transactions for reimbursement purposes. Be sure to guide the agent through each step, ensuring clarity and confirming the completion of each task.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'Q8YZY1', 'cabin': 'business', 'flights': [{'flight_number': 'HAT133', 'date': '2024-05-16'}, {'flight_number': 'HAT220', 'date': '2024-05-17'}], 'payment_id': 'credit_card_8547862'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'Q8YZY1', 'total_baggages': 2, 'nonfree_baggages': 1, 'payment_id': 'credit_card_4134857'},
            ),
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': 'I9GT07'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="olivia_martin_3924",
        instruction="Your user id is olivia_martin_3924. You recently found out that your business meeting in Los Angeles has been rescheduled, and you need to adjust your travel plans accordingly. You have an existing reservation, DVONGW, that you wish to cancel as it no longer aligns with your updated schedule. \n\nAfter canceling, you want to book a round-trip flight from Denver (DEN) to Los Angeles (LAX) in the economy cabin. You prefer to depart on May 17, 2024, and return on May 18, 2024. Time is of particular importance to you; therefore, you want to ensure that your departure from Denver is in the early morning so you can make it to an afternoon meeting. You also have a preference for early afternoon flights for your return journey. Direct flights are preferable, but if not available, a one-stop flight is acceptable.\n\nFor payment, you have a $500 travel certificate and want to use it to cover the booking. Ensure that you use this certificate as your primary payment method, and if the certificate covers the full cost, no additional payment method is needed. Your total budget for the flight is limited to what the certificate can cover, so it's important the agent helps you find a flight within this budget.\n\nAdditionally, you have another reservation, H0MVIE. You have decided to bring an extra checked bag for this trip. Update the total baggage count to two, with one being a non-free baggage item. You want to use your Visa credit card ending in 7324 for any additional baggage fees incurred.\n\nYou are proactive in managing your travel arrangements and prefer to resolve these matters as soon as possible due to your tight schedule. You are content with the agent taking care of the calculations for any payment differences and baggage fees to ensure all changes stay within your budget without needing to provide further input. You generally do not prefer to provide personal information verbally as your user profile holds all necessary details.",
        actions=[
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': 'DVONGW'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'olivia_martin_3924', 'origin': 'DEN', 'destination': 'LAX', 'flight_type': 'round_trip', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT130', 'date': '2024-05-17'}, {'flight_number': 'HAT232', 'date': '2024-05-18'}], 'passengers': [{'first_name': 'Olivia', 'last_name': 'Martin', 'dob': '1990-04-05'}], 'payment_methods': [{'payment_id': 'certificate_5658877', 'amount': 284}], 'total_baggages': 1, 'nonfree_baggages': 0, 'insurance': 'no'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'H0MVIE', 'total_baggages': 2, 'nonfree_baggages': 1, 'payment_id': 'credit_card_1048722'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="0",
        user_id="ava_santos_3700",
        instruction="Your user id is ava_santos_3700. You are planning a business trip and need to update your existing reservation KZD31Z. You want to change your flights from economy to business class on May 18 and May 19. You have a tight schedule, so you prefer flights that leave after 10am CST to ensure you have enough time to prepare for meetings in the morning. You are specifically looking to book flights HAT149 and HAT056.\n\nYour membership is silver, and you have a gift card with $180 at your disposal. You want to use this gift card first to cover any additional costs. If the gift card balance is insufficient, you'll consider using another payment method you have on file, but only as a last resort. \n\nYou currently have 3 baggages included in your reservation, but you decided to add one more checked bag, making it a total of 4. However, you want to ensure that only one of these is a paid baggage due to the business class allowance.\n\nDue to a change in your travel needs, you must first cancel your existing reservation KZD31Z before rebooking to accommodate the updated flights and cabin class. You are traveling with a colleague, Daiki Jackson, whose details you have previously saved, and you don't need to provide his date of birth again.\n\nYou emphasize that you don't require travel insurance for this trip. You want to keep your travel plans flexible, so you're not focused on the cheapest option but rather on ensuring the itinerary fits your new schedule. If these modifications exceed your budget limitations on the gift card, you will evaluate the additional cost with your alternate payment methods.\n\nYou are reactive to the agent's questions and will provide additional details only if necessary. You prefer to keep the interaction concise and efficient, allowing the agent to perform calculations regarding payment and costs where needed.\n\nThis trip is crucial for an upcoming business engagement, so it's important that all changes are confirmed swiftly and accurately.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'KZD31Z', 'cabin': 'business', 'flights': [{'flight_number': 'HAT149', 'date': '2024-05-18'}, {'flight_number': 'HAT056', 'date': '2024-05-19'}], 'payment_id': 'gift_card_1756078'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'KZD31Z', 'total_baggages': 4, 'nonfree_baggages': 1, 'payment_id': 'gift_card_1756078'},
            ),
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': 'KZD31Z'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'ava_santos_3700', 'origin': 'IAH', 'destination': 'EWR', 'flight_type': 'round_trip', 'cabin': 'business', 'flights': [{'flight_number': 'HAT149', 'date': '2024-05-18'}, {'flight_number': 'HAT056', 'date': '2024-05-19'}], 'passengers': [{'first_name': 'Daiki', 'last_name': 'Jackson', 'dob': '1983-03-16'}], 'payment_methods': [{'payment_id': 'gift_card_1756078', 'amount': 574}], 'total_baggages': 3, 'nonfree_baggages': 0, 'insurance': 'no'},
            ),
        ],
        outputs=['327', '1000', '1786'],
    ),
    Task(
        annotator="3",
        user_id="anya_johansson_1855",
        instruction="Your user id is anya_johansson_1855. You are planning a trip that requires updating one of your existing reservations and making some new arrangements. Here's what you need:\n\n1. **Modify Existing Reservation:**\n   - You have an upcoming flight planned under reservation ID L0A0CE. You need to update this reservation to reflect a change in your travel plans. You prefer to fly in the economy class for this leg of your journey.\n   - You want to switch your flight to flight number HAT208, scheduled to depart on May 17, 2024. You're not concerned about the time of this flight as long as it is on the specified date.\n   - You have decided to use your Visa credit card ending in 2974 to cover any additional costs associated with this change.\n\n2. **Baggage Update:**\n   - For the same reservation (L0A0CE), you need to add one additional piece of baggage. This added baggage is not free, and you would like to pay for it using your gift card that has a balance of $149. \n\n3. **Cancel Unnecessary Reservation:**\n   - You realized that your plans have changed, and you no longer need the reservation under ID VAFQ3Q. Go ahead and cancel this reservation as part of streamlining your itinerary.\n\n4. **Book New Round-Trip Reservation:**\n   - You need to secure a round-trip flight departing from Newark Liberty International Airport (EWR) to Los Angeles (LAX). You want to fly in economy class.\n   - You are flexible with your schedule, but you must fly on May 17, 2024, with a return on May 19, 2024. The outbound flight should be flight number HAT041 and the return should be flight number HAT012.\n   - You will be traveling with Emma Gonzalez, whose travel details match yours, especially for the return.\n   - For payment, prioritize using your travel certificates first. Specifically, use the $100 certificate, then the two $150 certificates sequentially. If these do not completely cover your costs, charge the rest to your Visa credit card ending in 2974.\n   - You will have two pieces of baggage. While one is free, the second is chargeable, so please ensure that this is accounted for in the booking.\n   - You also want to purchase travel insurance for this trip to safeguard against any unforeseen circumstances.\n\n5. **Reactiveness and Additional Preferences:**\n   - You are proactive and prefer the agent to handle calculations and confirmations for you, especially regarding payment distributions and baggage fees.\n   - Due to privacy reasons, you do not prefer providing your date of birth, as it should already be on your profile.\n   - The urgency of these changes is high because of overlapping commitments, so prompt completion is crucial.\n\nBy following these detailed instructions, your travel plans should align perfectly with your current needs and preferences.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'L0A0CE', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT208', 'date': '2024-05-17'}], 'payment_id': 'credit_card_2114702'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'L0A0CE', 'total_baggages': 1, 'nonfree_baggages': 1, 'payment_id': 'gift_card_7865517'},
            ),
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': 'VAFQ3Q'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'anya_johansson_1855', 'origin': 'EWR', 'destination': 'LAX', 'flight_type': 'round_trip', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT041', 'date': '2024-05-17'}, {'flight_number': 'HAT012', 'date': '2024-05-19'}], 'passengers': [{'first_name': 'Anya', 'last_name': 'Johansson', 'dob': '1984-10-10'}, {'first_name': 'Emma', 'last_name': 'Gonzalez', 'dob': '1984-10-10'}], 'payment_methods': [{'payment_id': 'certificate_8387108', 'amount': 100}, {'payment_id': 'certificate_7696738', 'amount': 150}, {'payment_id': 'certificate_9039426', 'amount': 150}, {'payment_id': 'credit_card_2114702', 'amount': 306}], 'total_baggages': 2, 'nonfree_baggages': 1, 'insurance': 'yes'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="noah_lopez_2532",
        instruction="Your user id is noah_lopez_2532. You are planning a complex set of updates and new bookings for your upcoming travel itinerary and require assistance navigating these changes effectively.\n\nFirstly, you want to update your existing reservation with the ID E9E7HC to better suit your travel needs. You aim to fly in economy class on your upcoming trip. Your preference is for flights HAT077 and HAT233 on May 17, followed by HAT060 and HAT288 on May 18. You want to ensure you have a total of two checked bags for this trip, and you understand that both will incur an extra fee. You prefer to use your Visa credit card ending in 5999 for these transactions, ensuring seamless payment.\n\nAdditionally, you need to make a modification to your travel plans by canceling an existing reservation with ID 5XOFTB. You have decided this trip is no longer necessary and are looking to handle this cancellation efficiently.\n\nSubsequently, you're looking to book a new one-way reservation from Phoenix (PHX) to LaGuardia (LGA) on May 19. You desire to fly in business class for comfort and luxury. Your decision is influenced by a preference for a single direct flight, and you've identified flight HAT066 as the best option. This flight should depart at a time that allows you to have a relaxed morning, without any rush.\n\nFor this booking, you will apply your travel certificate worth $500. Given that the amount is more than sufficient to cover the cost of the flight, you will use it for the primary payment transaction. You wish to bring one checked bag on this new booking, for which a fee will apply. While you are generally cost-conscious, for this specific booking, you do not require travel insurance.\n\nThroughout this process, you prefer to be reactive, providing additional details only when asked. You prioritize smooth and efficient execution, aiming to avoid unnecessary complications. Given the various transactions involved, your primary motivation is to streamline your travel plans while maximizing the use of available resources and maintaining a balance of convenience and cost-effectiveness.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'E9E7HC', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT077', 'date': '2024-05-17'}, {'flight_number': 'HAT233', 'date': '2024-05-17'}, {'flight_number': 'HAT060', 'date': '2024-05-18'}, {'flight_number': 'HAT288', 'date': '2024-05-18'}], 'payment_id': 'credit_card_3623927'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'E9E7HC', 'total_baggages': 2, 'nonfree_baggages': 2, 'payment_id': 'credit_card_3623927'},
            ),
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': '5XOFTB'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'noah_lopez_2532', 'origin': 'PHX', 'destination': 'LGA', 'flight_type': 'one_way', 'cabin': 'business', 'flights': [{'flight_number': 'HAT066', 'date': '2024-05-19'}], 'passengers': [{'first_name': 'Noah', 'last_name': 'Lopez', 'dob': 'N/A'}], 'payment_methods': [{'payment_id': 'certificate_5542518', 'amount': 464}], 'total_baggages': 1, 'nonfree_baggages': 1, 'insurance': 'no'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="noah_martin_7498",
        instruction="Your user id is noah_martin_7498. You want to verify the seating arrangements for your reservation 6UJKDA to ensure comfort during your upcoming flight.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': '6UJKDA'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="harper_davis_5069",
        instruction="Your user id is harper_davis_5069. You want to verify the seating arrangements for reservation WLXS0L to ensure you have an aisle seat.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'WLXS0L'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="0",
        user_id="amelia_hernandez_8403",
        instruction="Your user id is amelia_hernandez_8403. You want to verify the seating arrangements and meal preferences for your reservation 5JR4XX to ensure a comfortable flight experience.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': '5JR4XX'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="2",
        user_id="ivan_kim_3844",
        instruction="Your user id is ivan_kim_3844. You want to ensure your seat preference is correctly updated for your reservation Q79V9W.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'Q79V9W'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="0",
        user_id="mia_thomas_5479",
        instruction="Your user id is mia_thomas_5479. You need to confirm the seat assignment for your reservation DYKWMO as you prefer a window seat.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'DYKWMO'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="anya_anderson_8280",
        instruction="Your user id is anya_anderson_8280. You want to confirm the seating arrangement for your reservation ZXIYE7 to ensure you have an aisle seat.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'ZXIYE7'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="anya_anderson_8280",
        instruction="Your user id is anya_anderson_8280. You want to confirm the seating arrangement for your reservation ZXIYE7 to ensure you have an aisle seat.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'ZXIYE7'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="2",
        user_id="mason_johansson_5154",
        instruction="Your user id is mason_johansson_5154. You have a couple of tasks related to your travel plans, and here's a detailed breakdown of what you need to accomplish:\n\n1. First, you need to get the details of your existing reservation with the ID RB9S17. This is important as you want to double-check the itinerary and possibly make some adjustments. \n\n2. Next, for your upcoming trip associated with the reservation ID 2OQQI6, you realized that you'll require additional luggage. Specifically, you need to update your reservation to include 2 total baggages, of which 1 is not a free carry-on. Use your Visa card ending in 2961 to pay for any additional fees. \n\n3. Additionally, you are planning another trip and want to search for direct flights from Denver (DEN) to Charlotte (CLT) on May 20, 2024. You're keen on a morning departure, aiming to arrive in Charlotte by early afternoon. You strongly prefer direct flights to avoid any potential layover complications.\n\n4. You have a new travel plan where you need to book a one-way flight for James Hernandez, departing from Philadelphia (PHL) to Charlotte (CLT) on May 19, 2024. Book in the economy class, and make sure there's no baggage or insurance added. James has a birthday on October 23, 1987, and you intend to use the Visa card ending in 1242, but if this is not possible, you should opt for any available alternative payment method that covers the amount of $199.\n\n5. After re-evaluating your plans, you decided to cancel the reservation with ID RB9S17. Ensure that any cancellation policies and potential fees are considered, and utilize any refunds according to the original payment method.\n\nFor these tasks, you are reactive to the agent's questions and will provide information only when explicitly asked. You are price-sensitive when it comes to luggage fees and prefer not to spend unnecessarily. Your travel plans are quite urgent due to a family gathering, so time efficiency is crucial. Finally, you prefer the agent to calculate any additional costs and present the best options for you, especially regarding payment strategies.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'RB9S17'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': '2OQQI6', 'total_baggages': 2, 'nonfree_baggages': 1, 'payment_id': 'credit_card_3358561'},
            ),
            Action(
                name="search_direct_flight",
                kwargs={'origin': 'DEN', 'destination': 'CLT', 'date': '2024-05-20'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'mason_johansson_5154', 'origin': 'PHL', 'destination': 'CLT', 'flight_type': 'one_way', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT269', 'date': '2024-05-19'}], 'passengers': [{'first_name': 'James', 'last_name': 'Hernandez', 'dob': '1987-10-23'}], 'payment_methods': [{'payment_id': 'credit_card_5590177', 'amount': 199}], 'total_baggages': 0, 'nonfree_baggages': 0, 'insurance': 'no'},
            ),
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': 'RB9S17'},
            ),
        ],
        outputs=['sample_output'],
    ),
    Task(
        annotator="0",
        user_id="yusuf_patel_4029",
        instruction="Your user id is yusuf_patel_4029. You have a membership status of regular and are planning a set of important business and personal trips. You are looking to update and manage your travel itinerary effectively. \n\nFor your upcoming trip, you have a reservation under the ID 7P3LPD that you need to adjust. You want to upgrade your seating to business class for a series of flights on May 16 and May 17, 2024. You prefer to travel in comfort as these are back-to-back flights, and business class will provide you with the necessary amenities to work on the go. You have already selected the following flights for this reservation: HAT204, HAT194, HAT006, and HAT107. Please ensure these updates are completed using your Mastercard ending in 6922 as the primary payment method.\n\nAdditionally, you have an existing reservation 847MY1, which you need to cancel. This trip is no longer necessary, and you prefer to utilize those funds towards your other travel needs.\n\nYou also need to book a new one-way flight from Philadelphia (PHL) to Chicago (ORD) on May 16, 2024, in economy class. You prefer early morning flights, ideally between 6 am and 9 am, to maximize your day in Chicago. For this booking, please use flight HAT197. This trip is personal, and you want to ensure you have a smooth journey, thus opting for one checked baggage. Include travel insurance since you prioritize peace of mind. Use your Visa credit card ending in 1576 for this transaction, ensuring it covers the amount of $207.\n\nRegarding your baggage needs, please update your reservation 7P3LPD to include a total of two pieces of baggage, with one being a nonfree baggage. For the baggage payment, please use an alternate payment method, preferably the same Mastercard ending in 6922 used previously for consistency.\n\nIn appreciation of your loyalty, you are eligible for a $50 travel certificate. Ensure this certificate is sent to you promptly as it may be useful for future travel plans.\n\nYou prefer to be proactive and ensure all steps are carried out accurately. You do not prefer providing unnecessary information beyond what's required, and you appreciate efficient and precise service. You want the agent to confirm each step and provide a summary to ensure all your instructions are followed correctly.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': '7P3LPD', 'cabin': 'business', 'flights': [{'flight_number': 'HAT204', 'date': '2024-05-17'}, {'flight_number': 'HAT194', 'date': '2024-05-16'}, {'flight_number': 'HAT006', 'date': '2024-05-17'}, {'flight_number': 'HAT107', 'date': '2024-05-17'}], 'payment_id': 'credit_card_5254946'},
            ),
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': '847MY1'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'yusuf_patel_4029', 'origin': 'PHL', 'destination': 'ORD', 'flight_type': 'one_way', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT197', 'date': '2024-05-16'}], 'passengers': [{'first_name': 'Yusuf', 'last_name': 'Patel', 'dob': 'unknown'}], 'payment_methods': [{'payment_id': 'credit_card_5254946', 'amount': 207}], 'total_baggages': 1, 'nonfree_baggages': 1, 'insurance': 'yes'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': '7P3LPD', 'total_baggages': 2, 'nonfree_baggages': 1, 'payment_id': 'credit_card_6642109'},
            ),
            Action(
                name="send_certificate",
                kwargs={'user_id': 'yusuf_patel_4029', 'amount': 50},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="0",
        user_id="raj_gonzalez_7490",
        instruction="Your user id is raj_gonzalez_7490. You have a reservation for an upcoming trip under the reservation ID MTCVDL, and you'd like to make some adjustments for an important business meeting. You're aiming to travel in business class for comfort, as you have a long day of meetings ahead. Your priority is to ensure that the flights are on May 20 for the outbound and May 24 for the return, aligning with your business schedule. You prefer flights HAT284 and HAT265 on May 20, and HAT275 and HAT259 on May 24, as they best fit within your meeting itineraries in terms of timing.\n\nYou would like to use your Mastercard credit card ending in 9177 for any additional costs associated with this upgrade. If the business class upgrade is not available for one or more flights, you'd prefer to remain in economy for those specific flights rather than change the schedule, as timing is critical.\n\nRegarding baggage, you plan to carry two pieces of luggage, which will both need to be checked in. You understand that these additional bags may incur fees, and you're ready to cover these with the same Mastercard mentioned earlier. You're reactive in your communication style and respond directly to questions posed by the agent, providing necessary details without going off-topic.\n\nTime is of the essence due to the proximity of your meeting dates, so you'd appreciate a swift confirmation of these changes. You don't want to provide personal details like your home address, as it's already on file. You wish for the agent to handle the calculations regarding any fare differences or additional baggage charges. Your goal is to streamline your travel experience so you can focus entirely on your professional commitments during this busy period.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'MTCVDL', 'cabin': 'business', 'flights': [{'flight_number': 'HAT284', 'date': '2024-05-20'}, {'flight_number': 'HAT265', 'date': '2024-05-20'}, {'flight_number': 'HAT275', 'date': '2024-05-24'}, {'flight_number': 'HAT259', 'date': '2024-05-24'}], 'payment_id': 'credit_card_5736502'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'MTCVDL', 'total_baggages': 2, 'nonfree_baggages': 2, 'payment_id': 'credit_card_5736502'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="0",
        user_id="chen_hernandez_2608",
        instruction="Your user id is chen_hernandez_2608. You have a busy week ahead with several travel commitments and need to make adjustments to your existing reservations and book a new trip. Your travel plans involve a blend of business and personal engagements, making your schedule quite tight.\n\nFirstly, you need to cancel your existing reservation with the ID TANH6H due to a change in your business meeting schedule. This is urgent as you want to avoid any cancellation fees.\n\nNext, you want to book a new round trip from Las Vegas (LAS) to Orlando (MCO) for a short vacation. You need to depart on May 16 and return either on May 18 or May 19. You prefer an economy cabin for this trip. Your flight preferences are as follows:\n- Departure should be after 10 AM to allow a morning meeting to conclude.\n- Return is flexible; if you can save money by staying an extra day, you will return on May 19.\n- You prefer direct flights, but one stopover is acceptable if it significantly reduces the price.\n\nYou plan to travel with your partner, Liam Nguyen (DOB: 1960-08-07). You both will carry one piece of baggage each, so a total of two baggages. Opt for travel insurance for this trip as it's a personal priority.\n\nRegarding payment, use your Mastercard credit card ending in 6680 for this booking. Your budget for this trip is $950, so you need the agent to ensure the total cost, including insurance, fits within this limit.\n\nAdditionally, you need to adjust the baggage allowance for your reservation V25KYO, which is for an upcoming conference. You will require a total of four baggages, with two being non-free. Use your Visa credit card ending in 7969 for any additional baggage charges incurred.\n\nFor your reservation OC39IW, you wish to modify the flight details to accommodate a sudden change in your business schedule. You need to change to the following flights, both in economy:\n- Adjust the flight to May 19 with flight number HAT197\n- Return on May 24 with flight number HAT289\nIf these changes result in a fare increase, use your Mastercard credit card ending in 6680 to cover the additional cost.\n\nYou are proactive and prefer to handle these changes swiftly to minimize disruptions to your schedule. Your focus is on ensuring that all modifications and new bookings align with your tight timetable and budget constraints. If there are any challenges in meeting these requirements, you want the agent to propose alternatives that best fit your needs.",
        actions=[
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': 'TANH6H'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'chen_hernandez_2608', 'origin': 'LAS', 'destination': 'MCO', 'flight_type': 'round_trip', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT137', 'date': '2024-05-16'}, {'flight_number': 'HAT214', 'date': '2024-05-18'}, {'flight_number': 'HAT259', 'date': '2024-05-19'}], 'passengers': [{'first_name': 'Chen', 'last_name': 'Hernandez', 'dob': '1980-01-15'}, {'first_name': 'Liam', 'last_name': 'Nguyen', 'dob': '1960-08-07'}], 'payment_methods': [{'payment_id': 'credit_card_8453507', 'amount': 932}], 'total_baggages': 2, 'nonfree_baggages': 0, 'insurance': 'yes'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'V25KYO', 'total_baggages': 4, 'nonfree_baggages': 2, 'payment_id': 'credit_card_6123046'},
            ),
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'OC39IW', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT197', 'date': '2024-05-19'}, {'flight_number': 'HAT289', 'date': '2024-05-24'}], 'payment_id': 'credit_card_8453507'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="2",
        user_id="harper_johnson_9249",
        instruction="Your user id is harper_johnson_9249. You are planning to update and book flights for an upcoming series of trips. You have a Gold membership, so you want to make sure you're maximizing its benefits, like free lounge access for business class flights. Here's what you need:\n\n1. **Update Existing Reservation (EB17TJ)**: \n   - You want to upgrade your cabin to business class for a more comfortable experience.\n   - You're restructuring your flights to include HAT083 on May 19, HAT221 on May 17, HAT282 on May 26, and HAT233 on May 18.\n   - You prefer to make this adjustment early in the day, before 10am to ensure you have time to plan.\n   - You want to use your Mastercard credit card ending in 4851 for this transaction since it offers travel insurance benefits.\n\n2. **Modify Reservation Baggage (DJ40OY)**:\n   - You need to add three bags to this reservation. You anticipate bringing extra luggage back from your travels.\n   - You will use your gift card with a balance of $272 to cover this cost, as you want to save other payment methods for potential flight changes or emergencies.\n\n3. **Book New Reservation (PHX to LGA)**:\n   - You are booking a one-way flight for Olivia Nguyen, flying on May 17. \n   - The flight should be in economy class. You prefer the first available morning flight to maximize her time in New York.\n   - You're cost-conscious for this leg, preferring the cheapest option available. \n   - You need to use your $100 travel certificate and then cover the remaining balance of $75 using the gift card with $290.\n   - No extra baggage or travel insurance is needed here, as Olivia is traveling light and doesn’t require additional coverage.\n\n**Payment Strategy**:\n- Always use certificates first to minimize out-of-pocket expenses.\n- Gift cards are your second preference for flexibility.\n- Your Mastercard is a fallback for any unexpected large expenses, keeping in mind that it provides certain travel protections.\n\n**Behavior & Preferences**:\n- You are proactive and detail-oriented. You want to ensure every transaction and booking is confirmed promptly.\n- You prefer not to repeat information that should be accessible through your user profile, like your birth date.\n- You want the agent to confirm all details and ensure all transactions are optimized for cost before proceeding.\n\n**Motivations & Urgency**:\n- The urgency stems from a desire to finalize travel plans well ahead of time, ensuring peace of mind and the ability to focus on work commitments closer to the date.\n- Personal comfort on long-haul flights motivates your preference for business class, and cost-efficiency drives your economy class decision for shorter flights.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'EB17TJ', 'cabin': 'business', 'flights': [{'flight_number': 'HAT083', 'date': '2024-05-19'}, {'flight_number': 'HAT221', 'date': '2024-05-17'}, {'flight_number': 'HAT282', 'date': '2024-05-26'}, {'flight_number': 'HAT233', 'date': '2024-05-18'}], 'payment_id': 'credit_card_6678874'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'DJ40OY', 'total_baggages': 3, 'nonfree_baggages': 3, 'payment_id': 'gift_card_5535249'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'harper_johnson_9249', 'origin': 'PHX', 'destination': 'LGA', 'flight_type': 'one_way', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT256', 'date': '2024-05-17'}], 'passengers': [{'first_name': 'Olivia', 'last_name': 'Nguyen', 'dob': '1966-05-16'}], 'payment_methods': [{'payment_id': 'gift_card_9320056', 'amount': 175}], 'total_baggages': 0, 'nonfree_baggages': 0, 'insurance': 'no'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="1",
        user_id="mei_hernandez_8984",
        instruction="Your user id is mei_hernandez_8984. You are preparing for an important business trip, and your schedule is tight, requiring careful travel planning. You have a reservation (ID: 1AKIA8) and just realized you need to update your baggage allowance due to recent changes in your luggage requirements. You need to add a total of 3 checked bags, of which 2 are non-free. You prefer to use your Mastercard credit card ending in 1698 for the non-free baggage fees, as you want to keep your other payment options flexible for future needs.\n\nIn addition, you are planning a one-way flight from Houston (IAH) to Chicago (ORD) on May 17, 2024, to attend a conference. You're looking for a morning departure, preferably no later than 10 am, to allow you to settle in before the event starts. You want to book in economy class and prefer direct flights to minimize travel time and stress. After reviewing your options, you've selected flight HAT044. \n\nSince your budget for this flight is a concern, you aim to use your available travel certificate valued at $250. However, you understand the flight cost is $169, and you want to utilize your certificate to cover this amount fully. You have no checked baggage for this new booking and have decided against purchasing travel insurance to keep costs down.\n\nIf the certificate cannot be used as intended, you would prefer the agent to inform you of alternatives. You assume the responsibility for payment calculations and rely on the agent to confirm transaction details. Since your schedule is hectic, you are reactive and will only provide additional information if specifically requested by the agent.",
        actions=[
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': '1AKIA8', 'total_baggages': 3, 'nonfree_baggages': 2, 'payment_id': 'credit_card_2140654'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'mei_hernandez_8984', 'origin': 'IAH', 'destination': 'ORD', 'flight_type': 'one_way', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT044', 'date': '2024-05-17'}], 'passengers': [{'first_name': 'Mei', 'last_name': 'Hernandez', 'dob': '1984-11-23'}], 'payment_methods': [{'payment_id': 'certificate_7502997', 'amount': 169}], 'total_baggages': 0, 'nonfree_baggages': 0, 'insurance': 'no'},
            ),
        ],
        outputs=['327', '1000', '1786'],
    ),
    Task(
        annotator="2",
        user_id="chen_martin_5489",
        instruction="Your user id is chen_martin_5489. You have a Gold membership and are planning a trip with a few changes, along with a new booking. Let’s break down your requirements:\n\n1. **Existing Reservation Update**:\n   - You want to modify your current reservation (ID: LYSE93) to switch both flights to the economy cabin. \n   - On May 19, you prefer to fly with flight numbers HAT006 and HAT100. \n   - You're already comfortable using your Mastercard ending in 6289 for any additional charges.\n\n2. **Baggage Adjustments**:\n   - You plan to travel with two pieces of baggage, but only one is non-free, and you're fine with the additional payment being charged to the same Mastercard.\n\n3. **Searching for Direct Flights**:\n   - You need to find a direct flight from Boston (BOS) to Seattle (SEA) on May 20. You emphasize the importance of avoiding layovers due to a tight schedule.\n   - While price is a consideration, the direct flight is the top priority.\n\n4. **New Booking**:\n   - After spending time in Seattle, you need to return to New York (JFK) on a one-way trip in the economy class. \n   - You’ve identified flight HAT258 on May 20. \n   - You'll be traveling alone, and all your personal details, including your date of birth (October 3, 1959), are available on your profile.\n   - For this booking, you will carry one bag, which is included with no additional charge for baggage.\n   - You prefer to forgo travel insurance to keep costs down.\n   - For payment, prioritize using the Mastercard ending in 6289, ensuring the total does not exceed $171.\n\n5. **Cancellation of Existing Reservation**:\n   - If your updated plans are successfully confirmed and align with your schedule, you wish to cancel your current reservation (ID: LYSE93) to avoid overlapping bookings and unnecessary charges.\n\n**Behavioral Preferences**:\n- You are generally reactive in communications, preferring concise interactions with agents.\n- You anticipate agents handling complex calculations and decisions, especially regarding price and logistics; your role is to provide necessary information when prompted.\n- Maintaining flexibility with flights and schedules is crucial due to potential last-minute changes in your itinerary.\n\nThis trip is significant as it aligns closely with personal commitments, requiring a seamless and efficient travel experience.",
        actions=[
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'LYSE93', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT006', 'date': '2024-05-19'}, {'flight_number': 'HAT100', 'date': '2024-05-19'}], 'payment_id': 'credit_card_3964469'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'LYSE93', 'total_baggages': 2, 'nonfree_baggages': 1, 'payment_id': 'credit_card_3964469'},
            ),
            Action(
                name="search_direct_flight",
                kwargs={'origin': 'BOS', 'destination': 'SEA', 'date': '2024-05-20'},
            ),
            Action(
                name="book_reservation",
                kwargs={'user_id': 'chen_martin_5489', 'origin': 'SEA', 'destination': 'JFK', 'flight_type': 'one_way', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT258', 'date': '2024-05-20'}], 'passengers': [{'first_name': 'Chen', 'last_name': 'Wilson', 'dob': '1959-10-03'}], 'payment_methods': [{'payment_id': 'credit_card_3964469', 'amount': 171}], 'total_baggages': 1, 'nonfree_baggages': 0, 'insurance': 'no'},
            ),
            Action(
                name="cancel_reservation",
                kwargs={'reservation_id': 'LYSE93'},
            ),
        ],
        outputs=[],
    ),
    Task(
        annotator="2",
        user_id="mason_johnson_9566",
        instruction="Your user id is mason_johnson_9566. You have a reservation ID YWZEQN for an upcoming business trip, and you want to make some changes to your travel plans. You are a Gold member and value comfort during your flights, so you prefer to upgrade to business class for this journey. You would like to change your flights to leave on May 18 for the first leg and return on May 27, with a final segment on May 28. Your preferred flights are HAT235, HAT214 on May 18, and HAT181, HAT217 for the return on May 27 and 28, respectively.\n\nYou want to ensure that none of your flights depart before 10 am local time to accommodate your morning routine. If those flights are unavailable, you are open to flights that depart in the late morning or early afternoon, provided they are in business class and do not significantly increase travel time. As a frequent traveler, you prefer minimizing layovers but are willing to consider them for significant cost savings.\n\nFor payment, your Mastercard credit card ending in 3523 is your primary method. However, you are mindful of your budget, so if the upgrade exceeds your anticipated budget, you want the agent to first check if any promotional vouchers or certificates associated with your Gold membership can be applied. Use your Mastercard only after exhausting these options. You would like the agent to confirm the final amount before processing payment.\n\nAdditionally, you want to include one checked bag for your trip. Since your membership covers a certain number of free bags, ensure that no unnecessary charges are applied. If there are charges, you prefer using the same payment strategy as above.\n\nYour approach to this interaction is proactive; you're keen to explore all available options but prefer not to dwell on unnecessary details. You rely on the agent to provide precise calculations and confirm all changes before finalizing. Your primary motivation for these changes is to ensure a comfortable and efficient travel experience for your important business trip.",
        actions=[
            Action(
                name="get_reservation_details",
                kwargs={'reservation_id': 'YWZEQN'},
            ),
            Action(
                name="update_reservation_flights",
                kwargs={'reservation_id': 'YWZEQN', 'cabin': 'business', 'flights': [{'flight_number': 'HAT235', 'date': '2024-05-18'}, {'flight_number': 'HAT214', 'date': '2024-05-18'}, {'flight_number': 'HAT181', 'date': '2024-05-27'}, {'flight_number': 'HAT217', 'date': '2024-05-28'}], 'payment_id': 'credit_card_3562064'},
            ),
            Action(
                name="update_reservation_baggages",
                kwargs={'reservation_id': 'YWZEQN', 'total_baggages': 1, 'nonfree_baggages': 0, 'payment_id': 'credit_card_3562064'},
            ),
        ],
        outputs=[],
    ),
]
