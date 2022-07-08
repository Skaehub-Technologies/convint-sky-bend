from faker import Faker

fake = Faker()

test_user = {
    "username": fake.user_name(),
    "password": fake.password(),
    "email": fake.email(),
}
test_user_2 = {
    "username": fake.user_name(),
    "password": fake.password(),
    "email": fake.email(),
}
