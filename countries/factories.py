import factory

from countries.models import Country


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Country

    country = factory.Sequence(lambda n: "Country %03d" % n)
