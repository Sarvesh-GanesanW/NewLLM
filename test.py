from faker import Faker
import pandas as pd
import random
# Set up Faker with a specific seed for reproducibility
fake = Faker()
Faker.seed(0)
random.seed(0)

# Function to generate a random dataset
def generate_random_dataset(num_rows=100):
    data = []

    for _ in range(num_rows):
        row = {
            'id': fake.uuid4(),
            'name': fake.name(),
            'age': random.randint(18, 60),
            'gender': random.choice(['M', 'F']),
            'occupation': fake.job(),
            'salary': random.uniform(30000, 100000),
            'location': fake.city(),
            'email': fake.email(),
            'phone_number': fake.phone_number(),
            'is_active': random.choice([True, False])
        }
        data.append(row)

    return pd.DataFrame(data)

# Generate a random dataset with 50 rows
random_df = generate_random_dataset(num_rows=50)

# Display the random dataset
print(random_df.head())

random_df.to_csv('random_data.csv', index=False)
