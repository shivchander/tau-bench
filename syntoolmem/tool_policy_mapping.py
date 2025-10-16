"""
Manual mapping of airline tools to their corresponding policy sections.

This mapping is used to provide context-specific policy information when generating
synthetic scenarios for each tool and argument combination.
"""

TOOL_POLICY_MAPPING = {
    "book_reservation": """## Book flight

- The agent must first obtain the user id, then ask for the trip type, origin, destination.

- Passengers: Each reservation can have at most five passengers. The agent needs to collect the first name, last name, and date of birth for each passenger. All passengers must fly the same flights in the same cabin.

- Payment: each reservation can use at most one travel certificate, at most one credit card, and at most three gift cards. The remaining amount of a travel certificate is not refundable. All payment methods must already be in user profile for safety reasons.

- Checked bag allowance: If the booking user is a regular member, 0 free checked bag for each basic economy passenger, 1 free checked bag for each economy passenger, and 2 free checked bags for each business passenger. If the booking user is a silver member, 1 free checked bag for each basic economy passenger, 2 free checked bag for each economy passenger, and 3 free checked bags for each business passenger. If the booking user is a gold member, 2 free checked bag for each basic economy passenger, 3 free checked bag for each economy passenger, and 3 free checked bags for each business passenger. Each extra baggage is 50 dollars.

- Travel insurance: the agent should ask if the user wants to buy the travel insurance, which is 30 dollars per passenger and enables full refund if the user needs to cancel the flight given health or weather reasons.""",

    "cancel_reservation": """## Cancel flight

- The agent must first obtain the user id, the reservation id, and the reason for cancellation (change of plan, airline cancelled flight, or other reasons)

- All reservations can be cancelled within 24 hours of booking, or if the airline cancelled the flight. Otherwise, basic economy or economy flights can be cancelled only if travel insurance is bought and the condition is met, and business flights can always be cancelled. The rules are strict regardless of the membership status. The API does not check these for the agent, so the agent must make sure the rules apply before calling the API!

- The agent can only cancel the whole trip that is not flown. If any of the segments are already used, the agent cannot help and transfer is needed.

- The refund will go to original payment methods in 5 to 7 business days.""",

    "update_reservation_flights": """## Modify flight - Change flights

- The agent must first obtain the user id and the reservation id.

- Change flights: Basic economy flights cannot be modified. Other reservations can be modified without changing the origin, destination, and trip type. Some flight segments can be kept, but their prices will not be updated based on the current price. The API does not check these for the agent, so the agent must make sure the rules apply before calling the API!

- Change cabin: all reservations, including basic economy, can change cabin without changing the flights. Cabin changes require the user to pay for the difference between their current cabin and the new cabin class. Cabin class must be the same across all the flights in the same reservation; changing cabin for just one flight segment is not possible.

- Payment: If the flights are changed, the user needs to provide one gift card or credit card for payment or refund method. The agent should ask for the payment or refund method instead.""",

    "update_reservation_baggages": """## Modify flight - Change baggage

- The agent must first obtain the user id and the reservation id.

- Change baggage and insurance: The user can add but not remove checked bags. The user cannot add insurance after initial booking.

- Checked bag allowance: If the booking user is a regular member, 0 free checked bag for each basic economy passenger, 1 free checked bag for each economy passenger, and 2 free checked bags for each business passenger. If the booking user is a silver member, 1 free checked bag for each basic economy passenger, 2 free checked bag for each economy passenger, and 3 free checked bags for each business passenger. If the booking user is a gold member, 2 free checked bag for each basic economy passenger, 3 free checked bag for each economy passenger, and 3 free checked bags for each business passenger. Each extra baggage is 50 dollars.

- Payment: User needs to provide one gift card or credit card for payment.""",

    "update_reservation_passengers": """## Modify flight - Change passengers

- The agent must first obtain the user id and the reservation id.

- Change passengers: The user can modify passengers but cannot modify the number of passengers. This is something that even a human agent cannot assist with.

- Passengers: Each reservation can have at most five passengers. The agent needs to collect the first name, last name, and date of birth for each passenger. All passengers must fly the same flights in the same cabin.""",

    "send_certificate": """## Refund

- If the user is silver/gold member or has travel insurance or flies business, and complains about cancelled flights in a reservation, the agent can offer a certificate as a gesture after confirming the facts, with the amount being $100 times the number of passengers.

- If the user is silver/gold member or has travel insurance or flies business, and complains about delayed flights in a reservation and wants to change or cancel the reservation, the agent can offer a certificate as a gesture after confirming the facts and changing or cancelling the reservation, with the amount being $50 times the number of passengers.

- Do not proactively offer these unless the user complains about the situation and explicitly asks for some compensation. Do not compensate if the user is regular member and has no travel insurance and flies (basic) economy.""",

    "get_user_details": """## Domain Basic

- Each user has a profile containing user id, email, addresses, date of birth, payment methods, reservation numbers, and membership tier.

The agent uses this tool to retrieve user information including their profile, payment methods, saved passengers, and existing reservations.""",

    "get_reservation_details": """## Domain Basic

- Each reservation has an reservation id, user id, trip type (one way, round trip), flights, passengers, payment methods, created time, baggages, and travel insurance information.

The agent uses this tool to retrieve complete reservation details including flights, passengers, payment history, baggage, and insurance.""",

    "search_direct_flight": """## Domain Basic - Flight Search

- Each flight has a flight number, an origin, destination, scheduled departure and arrival time (local time), and for each date:
  - If the status is "available", the flight has not taken off, available seats and prices are listed.
  - If the status is "delayed" or "on time", the flight has not taken off, cannot be booked.
  - If the status is "flying", the flight has taken off but not landed, cannot be booked.

The agent uses this tool to search for direct flights between two airports on a specific date.""",

    "search_onestop_flight": """## Domain Basic - Flight Search

- Each flight has a flight number, an origin, destination, scheduled departure and arrival time (local time), and for each date:
  - If the status is "available", the flight has not taken off, available seats and prices are listed.
  - If the status is "delayed" or "on time", the flight has not taken off, cannot be booked.
  - If the status is "flying", the flight has taken off but not landed, cannot be booked.

The agent uses this tool to search for one-stop flights (with a connection) between two airports on a specific date.""",

    "list_all_airports": """## Domain Basic - Airport Information

The agent uses this tool to retrieve all available airports and their IATA codes for flight booking and search.""",

    "calculate": """## General Tool

The agent uses this tool to perform numerical calculations when needed for pricing, refunds, or baggage fees.""",

    "think": """## General Tool

The agent uses this tool to reason through complex scenarios, plan multi-step actions, or verify policy compliance before taking action.

Related policies:
- Before taking any actions that update the booking database (booking, modifying flights, editing baggage, upgrading cabin class, or updating passenger information), you must list the action details and obtain explicit user confirmation (yes) to proceed.
- You should only make one tool call at a time, and if you make a tool call, you should not respond to the user simultaneously.""",

    "transfer_to_human_agents": """## General Tool - Escalation

The agent uses this tool when:
- You should transfer the user to a human agent if and only if the request cannot be handled within the scope of your actions.
- Any segments of a reservation are already used (cannot cancel partial trips)
- The user wants to modify the number of passengers
- The request violates policy and cannot be completed through available tools."""
}
