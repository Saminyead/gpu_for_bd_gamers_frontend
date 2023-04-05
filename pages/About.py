import streamlit as st

st.write(
    """
    # About This App   
    Are you a Bangladeshi gamer looking to buy a GPU? Do you wish you had a crystal ball to which you could just tell your budget, and
    it would just tell you what the best GPU in the market is right now? Then this app is the crystal ball for you! Right after the pandemic chip
    shortage ended, the dollar crisis started making the GPU prices in Bangladesh all over the place. Sometimes, newer generation products can be 
    had for less than older generation products (just compare the price of Radeon RX 6950 XT vs the RX 7900 XTX). Hopefully, this app will help 
    simplify the market research for you.
    """
)

st.header("How It Works")
st.write(
    """ 
    Data is collected across the websites of 9 of the largest computer hardware retailers of Bangladesh, and stored on to a database. When you 
    enter your budget, the app checks for the graphics card with the highest performance score, and present it to you. To choose which performance
    score, select the options "Yes" or "No" under the selection option "According to you, is Ray Tracing worth paying more for?", and then choose
    whether you want to consider both positive and negative traits of GPU, or if you are interested in the raw performance only. You can find more
    details about performance scores [here](https://github.com/Saminyead/gpu_for_bd_gamers/blob/master/docs/tier_score_simplified.md). Also, if you
    want to simply want to know all the information about a particular GPU in the market, then check the "All GPU Information" page.
    """
)

st.write("""
This is my first web application, and as a result may be a bit lacking in user experience. I hope to keep improving it, and add more features
for the benefit of Bangladeshi gamers. I hope this will help you get the best price-to-performance for your money.
""")