from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def solve_cvrp_ortools(node_dict, distance_matrix, vehicle_capacity, depot_id):
    node_ids = sorted(node_dict.keys())
    id_to_index = {node_id: i for i, node_id in enumerate(node_ids)}
    index_to_id = {i: node_id for node_id, i in id_to_index.items()}

    num_nodes = len(node_ids)

    data = {}
    data["distance_matrix"] = [
        [distance_matrix[i][j] for j in node_ids]
        for i in node_ids
    ]
    data["demands"] = [node_dict[i]["demand"] for i in node_ids]
    data["vehicle_capacities"] = [vehicle_capacity] * num_nodes
    data["num_vehicles"] = num_nodes
    data["depot"] = id_to_index[depot_id]

    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]),
        data["num_vehicles"],
        data["depot"]
    )

    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(data["distance_matrix"][from_node][to_node] * 1000)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data["demands"][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        data["vehicle_capacities"],
        True,
        "Capacity"
    )

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(search_parameters)

    routes = []

    if solution:
        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)

            route = []
            route_load = 0

            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                node_id = index_to_id[node_index]

                route.append(node_id)
                route_load += node_dict[node_id]["demand"]

                index = solution.Value(routing.NextVar(index))

            route.append(depot_id)

            if len(route) > 2:
                routes.append({
                    "vehicle_id": len(routes) + 1,
                    "route": route,
                    "load": route_load
                })

    return routes