import random as rand
import math
import bisect

class AdoptionCenter(object):
    """
    The AdoptionCenter class stores the important information that a
    client would need to know about, such as the different numbers of
    species stored, the location, and the name. It also has a method to adopt a pet.
    """

    def __init__(self, name, species_types, location):
        assert type(name) is str
        assert type(species_types) is dict
        assert type(location) is tuple

        self.name = name
        self.species_types = species_types
        self.location = location

    def get_number_of_species(self, animal):
        if animal in self.species_types:
            return self.species_types[animal]
        else:
            return 0

    def get_location(self):
        return self.location

    def get_name(self):
        return self.name

    def adopt_pet(self, species):
        for x in self.species_types.keys(0):
            if self.species_types[x] <= 0:
                self.species_types[x].remove()
        self.species_types[species] -= 1


class Adopter(object):
    """
    Adopters represent people interested in adopting a species.
    They have a desired species type that they want, and their score is
    simply the number of species that the shelter has of that species.
    """

    def __init__(self, name, desired_species):
        self.name = name
        self.desired_species = desired_species
        self.score = '%.1f'

    def get_name(self):
        return self.name

    def get_desired_species(self):
        return self.desired_species

    def get_score(self, adoption_center):
        return adoption_center.get_number_of_species(self.desired_species)

    def get_score_other(self, adoption_center, other):
        return adoption_center.get_number_of_species(other)

    _get_score = get_score

class FlexibleAdopter(Adopter):
    """
    A FlexibleAdopter still has one type of species that they desire,
    but they are also alright with considering other types of species.
    considered_species is a list containing the other species the adopter will consider
    Their score should be 1x their desired species + .3x all of their desired species
    """

    def __init__(self, name, desired_species, considered_species):
        super(FlexibleAdopter, self).__init__(name, desired_species)
        self.considered_species = considered_species

    def get_score(self, adoption_center):
        score = self._get_score(adoption_center) + 0.3 * sum(
            [self.get_score_other(adoption_center, x) for x in self.considered_species])
        return self.score % score


class FearfulAdopter(Adopter):
    """
    A FearfulAdopter is afraid  a particular species of animal.
    If the adoption center has one or more of those animals in it, they will
    be a bit more reluctant to go there due to the presence of the feared species.
    Their score should be 1x number of desired species - .3x the number of feared species
    """

    def __init__(self, name, desired_species, feared_species):
        super(FearfulAdopter, self).__init__(name, desired_species)
        if type(feared_species) != list:
            self.feared_species = [feared_species]
        else:
            self.feared_species = feared_species

    def get_score(self, adoption_center):
        score = self._get_score(adoption_center) - (
            0.3 * sum([self.get_score_other(adoption_center, x) for x in self.feared_species]))
        return self.score % score


class AllergicAdopter(Adopter):
    """
    An AllergicAdopter is extremely allergic to a one or more species and cannot
    even be around it a little bit! If the adoption center contains one or more of
    these animals, they will not go there.
    Score should be 0 if the center contains any of the animals, or 1x number of desired animals if not
    """

    def __init__(self, name, desired_species, allergic_species):
        super(AllergicAdopter, self).__init__(name, desired_species)

        if type(allergic_species) != list:
            self.allergic_species = [allergic_species]
        else:
            self.allergic_species = allergic_species

    def get_score(self, adoption_center):
        if all(not adoption_center.get_number_of_species(i) for i in self.allergic_species):
            score = self._get_score(adoption_center)
            return self.score % score
        return 0


class MedicatedAllergicAdopter(AllergicAdopter):
    """
    A MedicatedAllergicAdopter is extremely allergic to a particular species
    However! They have a medicine of varying effectiveness, which will be given in a dictionary
    To calculate the score for a specific adoption center, we want to find what is the most allergy-inducing species that the adoption center has for the particular MedicatedAllergicAdopter.
    To do this, first examine what species the AdoptionCenter has that the MedicatedAllergicAdopter is allergic to, then compare them to the medicine_effectiveness dictionary.
    Take the lowest medicine_effectiveness found for these species, and multiply that value by the Adopter's calculate score method.
    """

    def __init__(self, name, desired_species, allergic_species, medicine_effectiveness):
        super(MedicatedAllergicAdopter, self).__init__(name, desired_species, allergic_species)
        assert type(medicine_effectiveness) == dict
        self.medicine_effectiveness = medicine_effectiveness

    def get_score(self, adoption_center):
        if all(not adoption_center.get_number_of_species(i) for i in self.allergic_species):
            score = self._get_score(adoption_center)
            return self.score % score
        else:
            coefficient = min([self.medicine_effectiveness[i] if i in self.medicine_effectiveness else 1 for i in
                               [x if adoption_center.get_number_of_species(x) else 0 for x in self.allergic_species]])
            score = coefficient * self._get_score(adoption_center)
            return self.score % score


class SluggishAdopter(Adopter):
    """
    A SluggishAdopter really dislikes travelling. The further away the
    AdoptionCenter is linearly, the less likely they will want to visit it.
    Since we are not sure the specific mood the SluggishAdopter will be in on a
    given day, we will assign their score with a random modifier depending on
    distance as a guess.
    Score should be
    If distance < 1 return 1 x number of desired species
    elif distance < 3 return random between (.7, .9) times number of desired species
    elif distance < 5. return random between (.5, .7 times number of desired species
    else return random between (.1, .5) times number of desired species
    """

    def __init__(self, name, desired_species, location):
        super(SluggishAdopter, self).__init__(name, desired_species)
        self.location = location

    def distance(self, adoption_center):
        distance = math.sqrt((adoption_center.get_location()[0] - self.location[0]) ** 2 + (
            adoption_center.get_location()[1] - self.location[1]) ** 2)
        return distance

    def get_score(self, adoption_center):
        """
        Using bisection search of ordered list [1,3,5,7] to map distance to coefficient
        example: (bisect.bisect(breakpoints,distance) - 1) for distance = 2.43 will return 1
                  then it will be mapped to mapping[1] - the coefficient needed.

        :param adoption_center: AdotptionCenter object
        :return float: score
        """
        score = self._get_score(adoption_center)
        distance = self.distance(adoption_center)
        mapping = [1, rand.uniform(0.7, 0.9), rand.uniform(0.5, 0.7), rand.uniform(0.1, 0.5)]
        breakpoints = [1,3,5,7]
        return self.score % (score * mapping[bisect.bisect(breakpoints,distance) - 1])

def get_ordered_adoption_center_list(adopter, list_of_adoption_centers):
    """
    The method returns a list of an organized adoption_center such that the scores for each AdoptionCenter to the Adopter will be ordered from highest score to lowest score.
    """
    sorted_ac = sorted({i.get_name(): adopter.get_score(i) for i in list_of_adoption_centers}.items(), key=lambda x: (float(x[1]), x[0]), reverse=True)
    return dict([(adopter.get_name(), sorted_ac)])


def get_adopters_for_advertisement(adoption_center, list_of_adopters, n):
    """
    The function returns a list of the top n scoring Adopters from list_of_adopters (in numerical order of score)
    """
    sorted_adopters = sorted({i.get_name(): i.get_score(adoption_center) for i in list_of_adopters}.items(),
                             key=lambda x: (float(x[1]), x[0]), reverse=True)
    return dict([(adoption_center.get_name(), sorted_adopters[:n])])


adopter = MedicatedAllergicAdopter("One", "Cat", ['Dog', 'Horse'], {"Dog": .5, "Horse": 0.2})
adopter2 = Adopter("Two", "Cat")
adopter3 = FlexibleAdopter("Three", "Horse", ["Lizard", "Cat"])
adopter4 = FearfulAdopter("Four", "Cat", "Dog")
adopter5 = SluggishAdopter("Five", "Cat", (1, 2))
adopter6 = AllergicAdopter("Six", "Cat", "Dog")

ac = AdoptionCenter("Place1", {"Mouse": 12, "Dog": 2}, (1, 1))
ac2 = AdoptionCenter("Place2", {"Cat": 12, "Lizard": 2}, (3, 5))
ac3 = AdoptionCenter("Place3", {"Horse": 25, "Dog": 9}, (-2, 10))

# how to test get_adopters_for_advertisement
print get_adopters_for_advertisement(ac, [adopter, adopter2, adopter3, adopter4, adopter5, adopter6], 10)
# you can print the name and score of each item in the list returned

adopter4 = FearfulAdopter("Four", "Cat", "Dog")
adopter5 = SluggishAdopter("Five", "Cat", (1, 2))
adopter6 = AllergicAdopter("Six", "Lizard", "Cat")

ac = AdoptionCenter("Place1", {"Cat": 12, "Dog": 2}, (1, 1))
ac2 = AdoptionCenter("Place2", {"Cat": 12, "Lizard": 2}, (3, 5))
ac3 = AdoptionCenter("Place3", {"Cat": 40, "Dog": 4}, (-2, 10))
ac4 = AdoptionCenter("Place4", {"Cat": 33, "Horse": 5}, (-3, 0))
ac5 = AdoptionCenter("Place5", {"Cat": 45, "Lizard": 2}, (8, -2))
ac6 = AdoptionCenter("Place6", {"Cat": 23, "Dog": 7, "Horse": 5}, (-10, 10))

adopter5.get_score(ac3)
# how to test get_ordered_adoption_center_list
print get_ordered_adoption_center_list(adopter4, [ac, ac2, ac3, ac4, ac5, ac6])
# you can print the name and score of each item in the list returned
