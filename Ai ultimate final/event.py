"""Simulation Events

This file should contain all the classes necessary to model the different
kinds of events in the simulation.
"""
from __future__ import annotations
from typing import List

from rider import Rider, WAITING, CANCELLED, SATISFIED
from dispatcher import Dispatcher
from driver import Driver
from location import deserialize_location
from monitor import Monitor, RIDER, DRIVER, REQUEST, CANCEL, PICKUP, DROPOFF


class Event:
    """An event.

    Events have an ordering that is based on the event timestamp: Events with
    older timestamps are less than those with newer timestamps.

    This class is abstract; subclasses must implement do().

    You may, if you wish, change the API of this class to add
    extra public methods or attributes. Make sure that anything
    you add makes sense for ALL events, and not just a particular
    event type.

    Document any such changes carefully!

    === Attributes ===
    timestamp: A timestamp for this event.
    """

    timestamp: int

    def __init__(self, timestamp: int) -> None:
        """Initialize an Event with a given timestamp.

        Precondition: timestamp must be a non-negative integer.

        >>> Event(7).timestamp
        7
        """
        self.timestamp = timestamp

    # The following six 'magic methods' are overridden to allow for easy
    # comparison of Event instances. All comparisons simply perform the
    # same comparison on the 'timestamp' attribute of the two events.
    def __eq__(self, other: Event) -> bool:
        """Return True iff this Event is equal to <other>.

        Two events are equal iff they have the same timestamp.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first == second
        False
        >>> second.timestamp = first.timestamp
        >>> first == second
        True
        """
        return self.timestamp == other.timestamp

    def __ne__(self, other: Event) -> bool:
        """Return True iff this Event is not equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first != second
        True
        >>> second.timestamp = first.timestamp
        >>> first != second
        False
        """
        return not self == other

    def __lt__(self, other: Event) -> bool:
        """Return True iff this Event is less than <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first < second
        True
        >>> second < first
        False
        """
        return self.timestamp < other.timestamp

    def __le__(self, other: Event) -> bool:
        """Return True iff this Event is less than or equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first <= first
        True
        >>> first <= second
        True
        >>> second <= first
        False
        """
        return self.timestamp <= other.timestamp

    def __gt__(self, other: Event) -> bool:
        """Return True iff this Event is greater than <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first > second
        False
        >>> second > first
        True
        """
        return not self <= other

    def __ge__(self, other: Event) -> bool:
        """Return True iff this Event is greater than or equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first >= first
        True
        >>> first >= second
        False
        >>> second >= first
        True
        """
        return not self < other

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        raise NotImplementedError("Implemented in a subclass")

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Do this Event.

        Update the state of the simulation, using the dispatcher, and any
        attributes according to the meaning of the event.

        Notify the monitor of any activities that have occurred during the
        event.

        Return a list of new events spawned by this event (making sure the
        timestamps are correct).

        Note: the "business logic" of what actually happens should not be
        handled in any Event classes.

        """
        raise NotImplementedError("Implemented in a subclass")


class RiderRequest(Event):
    """A rider requests a driver.

    === Attributes ===
    rider: The rider.
    """

    rider: Rider

    def __init__(self, timestamp: int, rider: Rider) -> None:
        """Initialize a RiderRequest event.

        """
        super().__init__(timestamp)
        self.rider = rider

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Assign the rider to a driver or add the rider to a waiting list.
        If the rider is assigned to a driver, the driver starts driving to
        the rider.

        Return a Cancellation event. If the rider is assigned to a driver,
        also return a Pickup event.

        """
        monitor.notify(self.timestamp, RIDER, REQUEST,
                       self.rider.id, self.rider.origin)

        events = []
        driver = dispatcher.request_driver(self.rider)
        if driver is not None:
            travel_time = driver.start_drive(self.rider.origin)
            events.append(Pickup(self.timestamp + travel_time,
                                 self.rider, driver))
        events.append(Cancellation(self.timestamp + self.rider.patience,
                                   self.rider))
        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return "{} -- {}: Request a driver".format(self.timestamp, self.rider)


class DriverRequest(Event):
    """A driver requests a rider.

    === Attributes ===
    driver: The driver.
    """

    driver: Driver

    def __init__(self, timestamp: int, driver: Driver) -> None:
        """Initialize a DriverRequest event.

        """
        super().__init__(timestamp)
        self.driver = driver

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Register the driver, if this is the first request, and
        assign a rider to the driver, if one is available.

        If a rider is available, return a Pickup event.

        """
        # Notify the monitor about the request.

        # Request a rider from the dispatcher.
        # If there is one available, the driver starts driving towards the
        # rider, and the method returns a Pickup event for when the driver
        # arrives at the rider's location.
        monitor.notify(self.timestamp, DRIVER, REQUEST,
                       self.driver.id, self.driver.location)
        events = []
        rider = dispatcher.request_rider(self.driver)
        # Assign a Cancel/ Pickup event based on the travel time
        if rider is not None:
            travel_time = self.driver.start_drive(rider.origin)
            if travel_time > rider.patience:
                dispatcher.cancel_ride(rider)
                events.append(Cancellation(self.timestamp + rider.patience,
                                           rider))
                self.driver.is_idle = True
            events.append(Pickup(self.timestamp + travel_time,
                                 rider, self.driver))
        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return "{} -- {}: Request a rider".format(self.timestamp, self.driver)


class Cancellation(Event):
    """A rider cancels a ride.

    === Attributes ===
    timestamp: The time when the rider cancels their ride.
    rider: The Rider

    """
    timestamp: int
    rider: Rider

    def __init__(self, timestamp: int, rider: Rider) -> None:
        super().__init__(timestamp)
        self.rider = rider

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        events = []
        if self.rider.status == WAITING:
            self.rider.status = CANCELLED
            monitor.notify(self.timestamp, RIDER, CANCEL,
                           self.rider.id, self.rider.origin)
            return events
        else:
            return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return "{} -- {}: Cancels a driver".format(self.timestamp, self.rider)


class Pickup(Event):
    """A driver picks up a rider.

    === Attributes ===
    timestamp: The time when the driver picks up the rider.
    rider: The Rider
    driver: The Driver

    """
    rider: Rider
    driver: Driver

    def __init__(self, timestamp: int, rider: Rider, driver: Driver) -> None:
        super().__init__(timestamp)
        self.rider = rider
        self.driver = driver

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        events = []
        if self.rider.status == WAITING:
            self.rider.status = SATISFIED
            self.driver.location = self.rider.origin
            self.driver.destination = self.rider.destination
            # notify the monitor about the driver
            monitor.notify(self.timestamp, DRIVER, PICKUP,
                           self.driver.id, self.driver.location)
            # notify the monitor about the rider
            monitor.notify(self.timestamp, RIDER, PICKUP,
                           self.rider.id, self.rider.origin)

            travel_time = self.driver.start_ride(self.rider)
            events.append(
                Dropoff(self.timestamp + travel_time, self.rider, self.driver))

        elif self.rider.status == CANCELLED:
            self.driver.location = self.rider.origin
            self.driver.destination = None
            monitor.notify(self.timestamp, DRIVER, CANCEL,
                           self.driver.id, self.driver.location)
            events.append(DriverRequest(self.timestamp, self.driver))

        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return f"{self.driver} picks up {self.rider} at {self.timestamp}"


class Dropoff(Event):
    """A driver drops off a rider.

    === Attributes ===
    timestamp: The time when the driver drops off the rider.
    rider: The Rider
    driver: The Driver

    """
    timestamp: int
    rider: Rider
    driver: Driver

    def __init__(self, timestamp: int, rider: Rider, driver: Driver) -> None:
        super().__init__(timestamp)
        self.rider = rider
        self.driver = driver

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        events = []
        self.driver.location = self.rider.destination
        self.driver.end_ride()
        monitor.notify(self.timestamp, DRIVER, DROPOFF,
                       self.driver.id, self.driver.location)
        monitor.notify(self.timestamp, RIDER, DROPOFF,
                       self.rider.id, self.rider.destination)
        events.append(DriverRequest(self.timestamp, self.driver))
        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return f"{self.driver} drops {self.rider} at {self.timestamp}"


def create_event_list(filename: str) -> List[Event]:
    """Return a list of Events based on raw list of events in <filename>.

    Precondition: the file stored at <filename> is in the format specified
    by the assignment handout.

    filename: The name of a file that contains the list of events.
    """
    events = []
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            tokens = line.split()
            timestamp = int(tokens[0])
            event_type = tokens[1]

            if event_type == "DriverRequest":
                driver_id = tokens[2]
                loc = deserialize_location(tokens[3])
                speed = int(tokens[4])
                driver = Driver(driver_id, loc, speed)
                events.append(DriverRequest(timestamp, driver))

            elif event_type == "RiderRequest":
                driver_id = tokens[2]
                origin = deserialize_location(tokens[3])
                destination = deserialize_location(tokens[4])
                patience = int(tokens[5])
                rider = Rider(driver_id, patience, origin, destination)
                events.append(RiderRequest(timestamp, rider))

    return events


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(
        config={
            'allowed-io': ['create_event_list'],
            'extra-imports': ['rider', 'dispatcher', 'driver',
                              'location', 'monitor']})
