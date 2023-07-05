"""Drivers for the simulation"""


from typing import Optional
from location import Location, manhattan_distance
from rider import Rider


class Driver:
    """A driver for a ride-sharing service.

    === Attributes ===
    id: A unique identifier for the driver.
    location: The current location of the driver.
    is_idle: True if the driver is idle and False otherwise.
    """

    id: str
    location: Location
    is_idle: bool
    speed: int
    destination: Optional[Location]

    def __init__(self, identifier: str, location: Location, speed: int) -> None:
        """Initialize a Driver.

        """
        self.id = identifier
        self.location = location
        self.is_idle = False
        self.speed = speed
        self.destination = None

    def __str__(self) -> str:
        """Return a string representation.

        """
        return f"{self.id} is at {self.location} with a speed of {self.speed}"

    def __eq__(self, other: object) -> bool:
        """Return True if self equals other, and false otherwise.

        """
        if isinstance(other, Driver):
            return self.id == other.id
        return False

    def get_travel_time(self, destination: Location) -> int:
        """Return the time it will take to arrive at the destination,
        rounded to the nearest integer.

        """
        distance = manhattan_distance(self.location, destination)
        return round(distance / self.speed)

    def start_drive(self, location: Location) -> int:
        """Start driving to the location.
        Return the time that the drive will take.

        """
        self.destination = location
        self.is_idle = False
        time = self.get_travel_time(location)
        return time

    def end_drive(self) -> None:
        """End the drive and arrive at the destination.

        Precondition: self.destination is not None.

        """
        self.location = self.destination
        self.destination = None

    def start_ride(self, rider: Rider) -> int:
        """Start a ride and return the time the ride will take.

        """
        self.destination = rider.destination
        time = self.get_travel_time(rider.destination)
        return time

    def end_ride(self) -> None:
        """End the current ride, and arrive at the rider's destination.

        Precondition: The driver has a rider.
        Precondition: self.destination is not None.

        """
        self.location = self.destination
        self.destination = None
        self.is_idle = True


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(
        config={'extra-imports': ['location', 'rider']})
