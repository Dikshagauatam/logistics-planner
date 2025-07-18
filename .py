import math

class TransportMode:
    """
    Represents a mode of transport with its base speed and cost factor.
    Speed is in km/h. Cost factor is per km.
    """
    def _init_(self, name, base_speed_kmph, cost_per_km):
        self.name = name
        self.base_speed_kmph = base_speed_kmph
        self.cost_per_km = cost_per_km

    def _str_(self):
        return self.name

class Route:
    """
    Represents a possible route between two cities using a specific transport mode.
    Calculates base travel time and cost.
    """
    def _init_(self, origin, destination, mode, distance_km):
        self.origin = origin
        self.destination = destination
        self.mode = mode  # An instance of TransportMode
        self.distance_km = distance_km
        self.base_time_hours = self.distance_km / self.mode.base_speed_kmph
        self.base_cost = self.distance_km * self.mode.cost_per_km

    def _str_(self):
        return (f"Route from {self.origin} to {self.destination} via {self.mode.name} "
                f"(Distance: {self.distance_km:.2f} km, Base Time: {self.base_time_hours:.2f} hrs, "
                f"Base Cost: ₹{self.base_cost:.2f})")

class LogisticsPlanner:
    """
    Plans the best route and transport mode considering various factors.
    """
    def _init_(self):
        # Define available transport modes
        self.modes = {
            "Road": TransportMode("Road", base_speed_kmph=50, cost_per_km=10),
            "Rail": TransportMode("Rail", base_speed_kmph=40, cost_per_km=5),
            "Air": TransportMode("Air", base_speed_kmph=600, cost_per_km=50) # Air includes ground time to/from airports
        }

        # Define sample routes (simplified for demonstration)
        # In a real system, this would come from a database or mapping service
        self.routes = [
            Route("Delhi", "Mumbai", self.modes["Road"], 1400),
            Route("Delhi", "Mumbai", self.modes["Rail"], 1380), # Slightly different distance for rail
            Route("Delhi", "Mumbai", self.modes["Air"], 1150),  # Air distance

            Route("Mumbai", "Bengaluru", self.modes["Road"], 980),
            Route("Mumbai", "Bengaluru", self.modes["Rail"], 950),
            Route("Mumbai", "Bengaluru", self.modes["Air"], 840),

            Route("Delhi", "Kolkata", self.modes["Road"], 1500),
            Route("Delhi", "Kolkata", self.modes["Rail"], 1450),
            Route("Delhi", "Kolkata", self.modes["Air"], 1300),

            Route("Bengaluru", "Chennai", self.modes["Road"], 350),
            Route("Bengaluru", "Chennai", self.modes["Rail"], 360),
            # Air might not be practical for short distances, but included for completeness
            Route("Bengaluru", "Chennai", self.modes["Air"], 290),
        ]

        # Define impact factors for various conditions
        # These are multipliers applied to base time. 1.0 means no impact.
        self.impact_factors = {
            "weather": {
                "normal": 1.0,
                "moderate_rain": 1.15, # 15% increase in time
                "heavy_rain": 1.30,    # 30% increase
                "fog": 1.25,
                "cyclone": 2.0 # Significant delay or halt
            },
            "law_order": {
                "normal": 1.0,
                "minor_disruption": 1.10, # 10% increase
                "major_disruption": 1.30,
                "curfew": 2.5 # Very significant delay, potential halt
            },
            "strikes": {
                "none": 1.0,
                "local_strike": 1.20, # 20% increase
                "regional_strike": 1.50,
                "national_strike": 3.0 # Major halt
            },
            # Specific impacts for modes (e.g., road affected more by weather than rail)
            "mode_specific_impact": {
                "Road": {
                    "weather": {"heavy_rain": 1.4, "fog": 1.3}, # Road more affected by these
                    "law_order": {"curfew": 3.0},
                    "strikes": {"local_strike": 1.3, "regional_strike": 1.8}
                },
                "Rail": {
                    "weather": {"heavy_rain": 1.1, "fog": 1.05},
                    "law_order": {"curfew": 1.5},
                    "strikes": {"national_strike": 4.0} # Rail can be severely impacted by rail strikes
                },
                "Air": {
                    "weather": {"heavy_rain": 1.2, "fog": 1.3, "cyclone": 5.0}, # Air most affected by severe weather
                    "law_order": {"curfew": 1.1}, # Less direct impact
                    "strikes": {"national_strike": 3.0} # Air traffic control/airline strikes
                }
            }
        }

    def get_effective_impact_multiplier(self, conditions, mode_name):
        """
        Calculates the total time multiplier based on current conditions and mode.
        """
        total_multiplier = 1.0

        for factor_type, factor_value in conditions.items():
            if factor_type in self.impact_factors:
                # Apply general factor impact
                general_impact = self.impact_factors[factor_type].get(factor_value, 1.0)
                total_multiplier *= general_impact

                # Apply mode-specific factor impact if defined
                if mode_name in self.impact_factors["mode_specific_impact"]:
                    mode_factor_impacts = self.impact_factors["mode_specific_impact"][mode_name]
                    if factor_type in mode_factor_impacts:
                        mode_specific_value_impact = mode_factor_impacts[factor_type].get(factor_value, 1.0)
                        # We want to apply the difference or additional impact from mode_specific
                        # A simple way is to take the max or average, but for simplicity, let's
                        # just multiply the general impact by the mode-specific one.
                        # This means if general rain is 1.15 and road specific is 1.4 for heavy rain,
                        # the road will be 1.15 * 1.4 = 1.61. This might over-penalize.
                        # A better approach: take the maximum of general and specific for each factor.
                        total_multiplier = max(total_multiplier, general_impact * mode_specific_value_impact)
            else:
                print(f"Warning: Unknown condition factor type '{factor_type}'. Ignoring.")

        return total_multiplier

    def decide_route(self, origin_city, destination_city, current_conditions):
        """
        Decides the best route and transport mode.
        current_conditions is a dictionary like:
        {
            "weather": "heavy_rain",
            "law_order": "normal",
            "strikes": "none"
        }
        """
        possible_options = []

        print(f"\n--- Planning for {origin_city} to {destination_city} ---")
        print(f"Current Conditions: {current_conditions}")

        for route in self.routes:
            if route.origin == origin_city and route.destination == destination_city:
                # Calculate effective time based on conditions
                impact_multiplier = self.get_effective_impact_multiplier(current_conditions, route.mode.name)
                effective_time_hours = route.base_time_hours * impact_multiplier

                # For simplicity, cost is not impacted by these factors in this model,
                # but in a real scenario, delays can incur additional costs.
                effective_cost = route.base_cost

                possible_options.append({
                    "route": route,
                    "effective_time_hours": effective_time_hours,
                    "effective_cost": effective_cost,
                    "impact_multiplier": impact_multiplier
                })

        if not possible_options:
            print(f"No routes found from {origin_city} to {destination_city}.")
            return None

        # Sort options by effective time (lowest first)
        possible_options.sort(key=lambda x: x["effective_time_hours"])

        print("\nAvailable Options (sorted by effective time):")
        for option in possible_options:
            route = option["route"]
            print(f"  - Mode: {route.mode.name}, "
                  f"Base Time: {route.base_time_hours:.2f} hrs, "
                  f"Impact Multiplier: {option['impact_multiplier']:.2f}x, "
                  f"Effective Time: {option['effective_time_hours']:.2f} hrs, "
                  f"Effective Cost: ₹{option['effective_cost']:.2f}")

        best_option = possible_options[0]
        print("\n--- Recommendation ---")
        print(f"The best option is to use {best_option['route'].mode.name} from {origin_city} to {destination_city}.")
        print(f"  Estimated Effective Travel Time: {best_option['effective_time_hours']:.2f} hours")
        print(f"  Estimated Effective Cost: ₹{best_option['effective_cost']:.2f}")
        print(f"  (Base Time: {best_option['route'].base_time_hours:.2f} hrs, "
              f"Impact Multiplier: {best_option['impact_multiplier']:.2f}x due to current conditions)")

        return best_option

# --- Main execution ---
if __name__ == "_main_":
    planner = LogisticsPlanner()

    # Scenario 1: Normal conditions
    print("--- Scenario 1: Normal Conditions ---")
    conditions_normal = {
        "weather": "normal",
        "law_order": "normal",
        "strikes": "none"
    }
    planner.decide_route("Delhi", "Mumbai", conditions_normal)

    # Scenario 2: Heavy Rain and Minor Law & Order Disruption
    print("\n--- Scenario 2: Heavy Rain and Minor Law & Order Disruption ---")
    conditions_bad_weather = {
        "weather": "heavy_rain",
        "law_order": "minor_disruption",
        "strikes": "none"
    }
    planner.decide_route("Delhi", "Mumbai", conditions_bad_weather)
    planner.decide_route("Bengaluru", "Chennai", conditions_bad_weather)


    # Scenario 3: Regional Strike affecting Rail, but good weather
    print("\n--- Scenario 3: Regional Strike (affecting Rail) ---")
    conditions_strike = {
        "weather": "normal",
        "law_order": "normal",
        "strikes": "regional_strike"
    }
    planner.decide_route("Delhi", "Mumbai", conditions_strike)

    # Scenario 4: Cyclone (impacting Air most)
    print("\n--- Scenario 4: Cyclone ---")
    conditions_cyclone = {
        "weather": "cyclone",
        "law_order": "normal",
        "strikes": "none"
    }
    planner.decide_route("Mumbai", "Bengaluru", conditions_cyclone)

    # Scenario 5: National Strike (impacting Rail and Air significantly)
    print("\n--- Scenario 5: National Strike ---")
    conditions_national_strike = {
        "weather": "normal",
        "law_order": "normal",
        "strikes": "national_strike"
    }
    planner.decide_route("Delhi", "Kolkata", conditions_national_strike)