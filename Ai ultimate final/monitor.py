"""
The Monitor module contains the Monitor class, the Activity class,
and a collection of constants. Together the elements of the module
help keep a record of activities that have occurred.

Activities fall into two categories: Rider activities and Driver
activities. Each activity also has a description, which is one of
request, cancel, pickup, or dropoff.

=== Constants ===
RIDER: A constant used for the Rider activity category.
DRIVER: A constant used for the Driver activity category.
REQUEST: A constant used for the request activity description.
CANCEL: A constant used for the cancel activity description.
PICKUP: A constant used for the pickup activity description.
DROPOFF: A constant used for the dropoff activity description.

"""

from typing import Dict, List
from location import Location


RIDER = "rider"
DRIVER = "driver"

REQUEST = "request"
CANCEL = "cancel"
PICKUP = "pickup"
DROPOFF = "dropoff"


class Activity:
    """An activity that occurs in the simulation.

    === Attributes ===
    timestamp: The time at which the activity occurred.
    description: A description of the activity.
    identifier: An identifier for the person doing the activity.
    location: The location at which the activity occurred.
    """

    time: int
    description: str
    id: str
    location: Location

    def __init__(self, timestamp: int, description: str, identifier: str,
                 location: Location) -> None:
        """Initialize an Activity.

        """
        self.time = timestamp
        self.description = description
        self.id = identifier
        self.location = location


def _calculate_distance(location1: Location, location2: Location) -> int:
    """Calculate the distance between two locations."""
    x = abs(location2.row - location1.row)
    y = abs(location2.column - location1.column)
    return x + y


class Monitor:
    """A monitor keeps a record of activities that it is notified about.
    When required, it generates a report of the activities it has recorded.
    """

    # === Private Attributes ===
    _activities: Dict[str, Dict[str, List[Activity]]]
    #       A dictionary whose key is a category, and value is another
    #       dictionary. The key of the second dictionary is an identifier
    #       and its value is a list of Activities.

    def __init__(self) -> None:
        """Initialize a Monitor.

        """
        self._activities = {
            RIDER: {},
            DRIVER: {}
        }
        """@type _activities: dict[str, dict[str, list[Activity]]]"""

    def __str__(self) -> str:
        """Return a string representation.

        """
        return "Monitor ({} drivers, {} riders)".format(
            len(self._activities[DRIVER]), len(self._activities[RIDER]))

    def notify(self, timestamp: int, category: str, description: str,
               identifier: str, location: Location) -> None:
        """Notify the monitor of the activity.

        timestamp: The time of the activity.
        category: The category (DRIVER or RIDER) for the activity.
        description: A description (REQUEST | CANCEL | PICKUP | DROP_OFF)
            of the activity.
        identifier: The identifier for the actor.
        location: The location of the activity.
        """
        if identifier not in self._activities[category]:
            self._activities[category][identifier] = []

        activity = Activity(timestamp, description, identifier, location)
        self._activities[category][identifier].append(activity)

    def report(self) -> Dict[str, float]:
        """Return a report of the activities that have occurred.

        """
        return {"rider_wait_time": self._average_wait_time(),
                "driver_total_distance": self._average_total_distance(),
                "driver_ride_distance": self._average_ride_distance()}

    def _average_wait_time(self) -> float:
        """Return the average wait time of riders that have either been picked
        up or have cancelled their ride.

        """
        wait_time = 0
        count = 0
        for activities in self._activities[RIDER].values():
            # A rider that has less than two activities hasn't finished
            # waiting (they haven't cancelled or been picked up).
            if len(activities) >= 2:
                # The first activity is REQUEST, and the second is PICKUP
                # or CANCEL. The wait time is the difference between the two.
                wait_time += activities[1].time - activities[0].time
                count += 1
        return wait_time / count

    def _average_total_distance(self) -> float:
        """Return the average distance drivers have driven."""
        distance = 0
        count = 0

        for activities in self._activities[DRIVER].values():
            journies = []
            journey = []
            for i in activities:
                if i.description == REQUEST or i.description == PICKUP:
                    journey.append(i)
                elif i.description == DROPOFF or i.description == CANCEL:
                    journey.append(i)
                    temp = []
                    for j in journey:
                        temp.append(j)
                    journies.append(temp)
                    journey.clear()

            for j in journies:
                count += 1
                request_loc = None
                pickup_loc = None
                drop_loc = None
                cancel_loc = None

                for i in j:
                    if i.description == REQUEST:
                        request_loc = i.location
                    elif i.description == PICKUP:
                        pickup_loc = i.location
                    elif i.description == DROPOFF:
                        drop_loc = i.location
                    elif i.description == CANCEL:
                        cancel_loc = i.location

                if pickup_loc is None and drop_loc is None \
                        and cancel_loc is None:
                    pass

                if drop_loc is None and cancel_loc is not None:
                    distance += _calculate_distance(cancel_loc, request_loc)

                if drop_loc is None and pickup_loc is not None\
                        and cancel_loc is None:
                    distance += _calculate_distance(pickup_loc, request_loc)

                if drop_loc is not None:
                    pickup_distance = _calculate_distance(pickup_loc,
                                                          request_loc)
                    drop_distance = _calculate_distance(drop_loc, pickup_loc)
                    distance += pickup_distance + drop_distance

        return distance / count

    def _average_ride_distance(self) -> float:
        """Return the average distance drivers have driven on rides.

        """
        distance = 0
        count = 0
        for activities in self._activities[DRIVER].values():
            pickup_loc = None
            drop_loc = None
            for i in activities:
                if i.description == PICKUP:
                    pickup_loc = i.location
                elif i.description == DROPOFF:
                    drop_loc = i.location
            if pickup_loc is None or drop_loc is None:
                count += 1
            else:
                u = abs(drop_loc.row - pickup_loc.row)
                v = abs(drop_loc.column - pickup_loc.column)
                distance += u + v
                count += 1

        return distance / count


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(
        config={
            'max-args': 6,
            'extra-imports': ['typing', 'location']})
