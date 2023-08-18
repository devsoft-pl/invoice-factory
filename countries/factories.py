import factory

from countries.models import Country
from users.factories import UserFactory

A_UPPERCASE = ord("A")
ALPHABET_SIZE = 26


def _decompose(number):
    """Generate digits from `number` in base alphabet, least significants
    bits first.

    Since A is 1 rather than 0 in base alphabet, we are dealing with
    `number - 1` at each iteration to be able to extract the proper digits.
    """

    while number:
        number, remainder = divmod(number - 1, ALPHABET_SIZE)
        yield remainder


def base_10_to_alphabet(number):
    """
    Konwertuje liczbe na reprezentacje alfabetyczna,
    np.:
    liczba 1 zwraca A
    liczba 27 zwraca AA
    """

    return "".join(chr(A_UPPERCASE + part) for part in _decompose(number))[::-1]


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Country

    country = factory.Sequence(lambda n: f"Country {base_10_to_alphabet(n + 1)}")
    user = factory.SubFactory(UserFactory)


class CountryDictFactory(factory.DictFactory):
    country = factory.Sequence(lambda n: f"Country {base_10_to_alphabet(n + 1)}")
