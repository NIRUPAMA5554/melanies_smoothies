# Import python packages
import streamlit as st
import requests
import pandas as pd

cnx = st.connection("snowflake")

from snowflake.snowpark.functions import col


# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)


# Get the customer's name
name_on_order = st.text_input('Name on Smoothie:')

st.write(
    'The name on your Smoothie will be:',
    name_on_order
)


# Create Snowflake session
session = cnx.session()


# Get both FRUIT_NAME and SEARCH_ON from Snowflake
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)


# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()


# Choose up to 5 fruits
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5
)


# Process selected ingredients
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        # Add the customer-friendly fruit name to the order
        ingredients_string += fruit_chosen + ' '


        # Find the API search value for the selected fruit
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]


        # Display the search value
        st.write(
            'The search value for ',
            fruit_chosen,
            ' is ',
            search_on,
            '.'
        )


        # Display nutrition heading
        st.subheader(
            fruit_chosen + ' Nutrition Information'
        )


        # Call SmoothieFroot API using SEARCH_ON
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )


        # Display API response
        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )


    # Create the order SQL statement
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order)
        VALUES ('""" + ingredients_string + """','""" + name_on_order + """')
    """


    # Submit Order button
    time_to_insert = st.button('Submit Order')


    # Insert order into Snowflake
    if time_to_insert:

        session.sql(my_insert_stmt).collect()

        st.success(
            'Your Smoothie is ordered, ' + name_on_order + '!',
            icon="✅"
        )
