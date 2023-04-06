# GPU for BD Gamers Streamlit App
This is a web application that is made specifically for the gamers of Bangladesh, where they can simply put in their budget in BDT, and would get what is the 
highest performing graphics card they can buy. The application is made using Streamlit. It is the front-end of the [GPU for BD Gamers](https://github.com/Saminyead/gpu_for_bd_gamers)
project.

The app works by taking the budget of the user, and checking against a database which graphics card has the highest performance score that costs equal to, or
under that budget. It also checks whether or not there is a GPU that performs close (within 10% of the highest performing GPU) but costs much lower -- thus having
a higher performance-price ratio; as well as for a GPU that costs a little higher (within 20% of the highest performing GPU), but has a much higher performance score,
giving them a higher performance-price ratio as well. These graphics card along with their relevant information are then shown to the end-user. End users can also find 
information on any graphics card available in the market from the 'All GPU Information' page of the application.

The data in the database is collected on a daily basis from the websites of 9 of the largest computer hardware retailers (to see which, [see below](#list-of-hardware-retailers-for-data-collection)) of Bangladesh.
The graphics cards are then given some performance scores. How these performance scores are calculated can be found [here](https://github.com/Saminyead/gpu_for_bd_gamers/blob/master/docs/tier_score_simplified.md).
To know more about how the back-end processes of this app works, see this [repository](https://github.com/Saminyead/gpu_for_bd_gamers).

This the first data application that I have developed, and thus may be a bit lacking in the user experience. I will be continually working on it to make it better
and add more features.

### List of Hardware Retailers for Data Collection
1. Ryans Computer
2. Star Tech and Engineering
3. Tech Land BD
4. Skyland Computer BD
5. Nexus Technology
6. Global Brand
7. Ultra Technology
8. Creatus Computer
9. UCC Bangladesh
