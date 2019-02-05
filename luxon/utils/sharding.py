# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Christiaan Frans Rademan.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
"""Consistent hashing ring utilities module.

Consistent hashing on a ring is used by a lot of NoSQL type datastores use it.
The idea is that you have a ring that is numbered 0 to a huge number (2**22)
and the piece of data is assigned a number/slot on that ring. As you add new
nodes to the system they are given a number on that ring and will basically be
declared as the owner of certain range of 'slots' on that ring.
"""
from array import array
import math
from uuid import uuid4
from hashlib import md5
from struct import unpack_from

from luxon import GetLogger
from luxon.utils.encoding import if_bytes_to_unicode
from luxon.utils.objects import save, load
from luxon.exceptions import NotFoundError, DuplicateError

log = GetLogger(__name__)


def parse_zone(zone):
    """Validate zone name and format to str.

    Args:
        zone (str,int): zone name.

    Returns:
        str: Correctly formatted zone name.

    Raises:
        ValueError: Invalid zone name.
    """
    if isinstance(zone, int):
        zone = str(zone).lower()

    zone = if_bytes_to_unicode(zone)

    if not isinstance(zone, str):
        raise ValueError("Invalid Zone Name '%s'" % zone)

    return zone


def parse_id(node_id):
    """Validate node id and format to str.

    Args:
        node_id (str,int): node unique id.

    Returns:
        str: Correctly formatted node id.

    Raises:
        ValueError: Invalid node id.
    """
    if isinstance(node_id, int):
        node_id = str(node_id)

    node_id = if_bytes_to_unicode(node_id)

    if not isinstance(node_id, str):
        raise ValueError("Invalid ID '%s'" % node_id)

    return node_id


def parse_weight(weight):
    """Validate node weight and format to float.

    Args:
        weight (str,int,float): node weight.

    Returns:
        float: Correctly formatted node weight.

    Raises:
        ValueError: Invalid node weight.
    """
    try:
        weight = float(weight)
    except TypeError:
        raise ValueError("Invalid Weight '%s'" % weight)

    return weight


def get_slot(ring_power, data_id):
    """Obtain ring slot.

    This function uses consistent hashing to hash the 'data_id' provided.

    Since data ids are often textual names and not numbers, like paths for
    files or URLs, it makes sense to use a “real” hashing algorithm to
    convert the names to numbers first. The benefit of using a hashing
    algorithm like MD5 is that the resulting hashes have a known even
    distribution, meaning your ids will be evenly distributed.

    Since the 'slot' count is always a power of two, it is easy to use bit
    manipulation on the hash to determine the 'slot' rather than modulus. It
    isn’t much faster, but it is a little.

    The 'slot' shift value is known internally to the ring. This value is used
    to shift an MD5 hash of a 'data_id' to calculate the partition on which the
    data for that item should reside. Only the top four bytes of the hash are
    used in this process.

    We only byte shift the top four bytes of the hash with the 'ring_power'
    which defines the ring size.

    Any data_id values provided will be converted to string.

    Args:
        ring_power (int): Bits of ring size.
        data_id (int,str):  Unique id to hash to slot.

    Returns:
        int: Ring slot number.
    """
    data_id = str(data_id)
    slot_shift = 32 - ring_power
    return unpack_from(
        '>I',
        md5(data_id.encode()).digest())[0] >> slot_shift


def build_ring(nodes, ring_power, replica=None):
    """Build ring with slots.

    The slots are references to nodes and the total number of slots is
    determined by the ring_power. If the slot power is 16(bits) then
    65536 slots will be placed in a list known as the ring.

    If we have 2 nodes, and the ring_power is 16bits. Then node 1 will be
    placed in items range of 0 to 32767 and node 2 will be in items range
    of 32768 to 65535.

    get_slot(ring_power, data_id) function is used to select a node slot.

    Nodes are required to be a list / tuple. ( weight, node_id )

    Example of nodes list:
        [  ( 1.0, '1' ), ( 1.0, '2' ) ]

    The weight determines how to evenly distribute the nodes in the ring.
    If node 1 has double the weight of node 2, then effectively node 1 will
    occupy two thirds of the ring, while node 2 will only have one third of the
    ring.

    Example usage:
        .. code:: python

            nodes = [ ( 1.0, '1' ), ( 1.0, '2' ), ]

            ring = build_ring(nodes, 2)

            for node in ring:
                print(node)

    Args:
        nodes (list): List of nodes.
        ring_power (int): Bits of ring size.
        replica (int): Replica for informational purposes (logging).

    Returns:
        list: Ring.
    """
    ring = array('L')
    slots = 2 ** ring_power

    check_percent = [check for check in range(0, slots, math.ceil(slots / 4))]

    # Calculate Total Weight for all nodes.
    total_weight = sum([node[0] for node in nodes])

    # Iterate through all slots and create ring.
    slot = 0
    for node in nodes:
        weight = node[0]
        desired = math.ceil(slots / total_weight * weight)

        for _ in range(int(math.ceil(desired))):
            if slot in check_percent:
                percent_complete = round(100 * (float(slot)/float(slots)), 2)
                if replica is not None:
                    log.info("Building Replica Ring '%s' Completed '%s%s'" %
                             (replica, percent_complete, '%',))
                else:
                    log.info("Building Ring Completed '%s%s'" %
                             (percent_complete, '%',))
            if slot == slots:
                break

            ring.append(node[1])
            slot += 1

    if replica is not None:
        log.info("Building Replica Ring '%s' Completed '100%s'" %
                 (replica, '%',))
    else:
        log.info("Building Ring Completed '100%s'" %
                 ('%',))

    return ring


def build_empty_list(size):
    """Build empty List.

    Args:
        size (int): Size.

    Returns:
        list: List of size with 'None' values.
    """
    build = []
    for _ in range(size):
        build.append(None)

    return build


def build_empty_array(size):
    """Build empty array.

    Args:
        size (int): Size.

    Returns:
        Array: Array of size with 'None' values.
    """
    build = array('L')
    for _ in range(size):
        build.append(None)

    return build


class NodesTree(object):
    """NodesTree.

    Nodes and zones are stored in the NodesTree. Howeveer these are placed in
    prepared lists. The prepared list is a set of a empty items with a value of
    None. New nodes/zones are placed at the last empty entry. This is a
    deliberate attempt to ensure nodes/zones are within a consistant order and
    can be referenced by the index.

    All prepared lists are created based on the relevent size of the ring
    determined by the ring_power. The Ring Power has a direct impact on the
    maximum zones and nodes.

    The Ring provides the ability to:
        * Add/Updata/Delete zones.
        * Add/Updata/Delete nodes.
        * Ensure zones and nodes are always in consistant order.
        * Provide replica nodes for ring to build.

    Args:
        nodes_path (str): Load exisiting nodes from pickle file.
        ring_power (int): Bits for size of ring. (should never change)
        replicas (int): Duplicate nodes to distribute.
    """
    def __init__(self, nodes_path=None, ring_power=22, replicas=2):
        if nodes_path:
            nodes = load(nodes_path, 644)
            self._zones = nodes['zones']
            self._nodes = nodes['nodes']
            self._next_node = nodes['next_node']
            self._next_zone = nodes['next_zone']
            self._node_index = nodes['node_index']
            self._zone_index = nodes['zone_index']
            self._max_zones = nodes['max_zones']
            self._max_nodes = nodes['max_nodes']
            self._replicas = nodes['replicas']
        else:
            max_nodes = math.ceil((2 ** ring_power) / 16)
            if max_nodes < 1 + replicas:
                raise ValueError('Ring not sufficiant')

            max_zones = max(math.ceil(max_nodes / 1024),
                            replicas * 2)

            self._zones = build_empty_list(max_zones)
            self._nodes = build_empty_list(max_nodes)
            self._next_node = 0
            self._next_zone = 0
            self._node_index = {}
            self._zone_index = {}
            self._max_zones = max_zones
            self._max_nodes = max_nodes
            self._replicas = replicas

        log.info("NodesTree: Max Zones '%s' Max Nodes '%s' Replicas: '%s'" %
                 (self._max_zones,
                  self._max_nodes,
                  self._replicas,))

    def save(self, nodes_path):
        """Save nodes to pickle.

        Args:
            nodes_path (str): Path to ring pickle file.
        """
        nodes = {}
        nodes['zones'] = self._zones
        nodes['nodes'] = self._nodes
        nodes['next_node'] = self._next_node
        nodes['next_zone'] = self._next_zone
        nodes['node_index'] = self._node_index
        nodes['zone_index'] = self._zone_index
        nodes['max_zones'] = self._max_zones
        nodes['max_nodes'] = self._max_nodes
        nodes['replicas'] = self._replicas
        save(nodes, nodes_path, 644)

    def _take_empty_node_slot(self):
        # NOTE(cfrademan): Used to locate empty node in pre-build nodes slot.
        # This ensures new nodes are appended at to end. It also ensures if
        # nodes are removed that their references in the Ring will return None.
        for _ in range(self._max_nodes):
            next_node = self._next_node % self._max_nodes
            if self._nodes[next_node] is None:
                self._next_node += 1
                return next_node
            raise IndexError(
                "No empty slots for new node")

    def _take_empty_zone_slot(self):
        # NOTE(cfrademan): Used to locate empty zone in pre-build zones slot.
        # This ensures new nodes are appended at to end.
        for _ in range(self._max_zones):
            next_zone = self._next_zone % self._max_zones
            if self._zones[next_zone] is None:
                self._next_zone += 1
                return next_zone
            raise IndexError(
                "No empty slots for new zone")

    def add_zone(self, zone):
        """Add zone.

        Args:
            zone (str): Zone name.
        """
        zone = parse_zone(zone)
        if zone in self._zone_index:
            raise DuplicateError(
                "Adding duplicate zone '%s'" % zone)
        slot = self._take_empty_zone_slot()
        self._zones[slot] = (zone, array('L'),)
        self._zone_index[zone] = slot

    @property
    def zones(self):
        """Return zones.

        Returns:
            tuple: List of zones, zone being tuple ( 'name', slot )
        """
        return tuple(self._zone_index.items())

    @property
    def zones2nodes(self):
        """Zones to nodes.

        Provides a tuple of zones with nodes in each zone.
        """
        zones = []
        for zone_name in self._zone_index:
            nodes = []
            zone_slot = self._zone_index[zone_name]
            zone_slot_name, node_slots = self._zones[zone_slot]
            for node in node_slots:
                nodes.append(self._nodes[node])
            if nodes:
                zones.append(tuple(nodes))
        return tuple(zones)

    def rename_zone(self, zone, to_zone):
        """Rename zone to zone.

        Args:
            zone (str): Exisiting zone name.
            to_zone (str): New zone name.
        """
        zone = parse_zone(zone)
        to_zone = parse_zone(to_zone)
        if to_zone in self._zone_index:
            raise ValueError(
                "Rename to duplicate zone '%s'" % to_zone)
        if zone not in self._zone_index:
            raise ValueError(
                "Rname Zone not found '%s'" % zone)
        zone_slot = self._zone_index[zone]
        self._zones[zone_slot] = (to_zone, self._zones[zone_slot][1],)
        self._zone_index[to_zone] = self._zone_index.pop(zone)

    def delete_zone(self, zone):
        """Delete zone.

        Args:
            zone (str): Exisiting zone name.
        """
        zone = parse_zone(zone)
        if zone not in self._zone_index:
            raise ValueError(
                "Delete Zone not found '%s'" % zone)
        slot = self._zone_index[zone]
        if self._zones[slot][1]:
            raise ValueError(
                "Delete Zone not empty '%s'" % zone)
        del self._zone_index[zone]
        self._zones[slot] = None

    def get_zone_slot(self, zone):
        """Get zone slot.

        Args:
            zone (str): Exisiting Zone name.
        """
        try:
            return self._zone_index[zone]
        except KeyError:
            raise NotFoundError("Zone not found '%s'" % zone) from None

    def add_node(self, zone, weight=1, node_id=None, **kwargs):
        """Add node.

        Args:
            zone (str): Exisiting Zone name.
            weight (float/int): Weight for element.
            node_id (str): Unique ID or automatically provided UUID. (optional)
            **kwargs: Arbitrary options for nodes.

        Returns:
            dict: Node with property value pairs.
        """
        weight = parse_weight(weight)
        zone = parse_zone(zone)
        zone = self.get_zone_slot(zone)

        if node_id:
            if node_id in self._node_index:
                raise DuplicateError('Adding duplicate node_id')

            unique_id = node_id
        else:
            unique_id = str(uuid4())

        slot = self._take_empty_node_slot()

        node = {"node_id": str(unique_id), "zone": zone,
                "weight": weight, **kwargs, "node_slot": slot}

        self._node_index[unique_id] = (zone, slot,)
        self._zones[zone][1].append(slot)
        self._nodes[slot] = node

        return node

    def update_node(self, node_id, zone=None, weight=None, **kwargs):
        """Update node.

        Args:
            node_id (str): Unique Node Identifier.
            zone (str): Exisiting zone name.
            weight (float/int): Weight for element.
            **kwargs: Arbitrary options for nodes.

        Returns:
            dict: Node with property value pairs.
        """
        node = self.get_node(node_id, raw=True)
        if node:
            if weight:
                weight = parse_weight(weight)
                node['weight'] = weight

            if zone:
                zone = parse_zone(zone)
                new_zone_slot = self.get_zone_slot(zone)
                if new_zone_slot != node['zone']:
                    zone = self.get_zone_slot(zone)
                    slot = self._take_empty_node_slot()
                    old_zone_slot, old_node_slot = self._node_index[node_id]
                    self._zones[old_zone_slot][1][old_node_slot] = None
                    node['zone'] = new_zone_slot
                    node['node_slot'] = slot
                    self._node_index[node_id] = (zone, slot,)
                    self._nodes[slot] = node

            for kwarg in kwargs:
                node[kwarg] = kwargs[kwarg]

            return node

        else:
            raise NotFoundError(
                "Update node not found '%s'" % node_id)

    def _format_node(self, node):
        node = node.copy()
        zone = node['zone']
        node['zone'] = self._zones[zone][0]
        return node

    def get_nodes(self, raw=False):
        """Get all nodes.

        Args:
            raw (bool): If raw do not format for user-friendly view.

        Returns:
            tuple: All nodes.
        """
        nodes = []
        for node in self._node_index:
            zone, slot = self._node_index[node]
            if raw is False:
                nodes.append(self._format_node(
                    self._nodes[slot]))
            else:
                nodes.append(self._nodes[slot])

        return tuple(nodes)

    def get_node(self, node, raw=False):
        """Return node.

        Args:
            raw (bool): If raw do not format for user-friendly view.

        Returns:
            dict: Node with property value pairs.
        """
        if isinstance(node, int):
            node = self._nodes[node]
            if node:
                if raw is False:
                    return self._format_node(node)
                return node
        else:
            if node in self._node_index:
                zone, slot = self._node_index[node]
                if raw is False:
                    return self._format_node(self._nodes[slot])
                return self._nodes[slot]

    def delete_node(self, node_id):
        """Delete node.

        Args:
            node_id (str): Unique Node Identifier.
        """
        try:
            zone, slot = self._node_index[node_id]
        except KeyError:
            raise NotFoundError('Node not found') from None

        del self._node_index[node_id]
        self._nodes[slot] = None
        self._zones[zone][1].remove(slot)

    def build_replicates(self):
        """Build nodes into individual replicas for Ring Builder.

        Ring builder builds composite Rings where individual rings will be
        built for each replica. The purpose of this method is return the nodes
        grouped together for the composite rings.

        It is recommended that replicates is evenly deviseable between zones
        for even distribution and or replicates are equal zones.

        The algorithem ensures that no replicate has the same zone. If more
        replicates than zones, then it create copies of previous replicates
        within order. Its important to ensure replicates have unique zones as
        much as possible to ensure data is spread over the zones and not within
        the same zone only. If more zones than replicates then these are
        appended to replicates.

        Returns:
            list: replica to nodes.
        """
        def format_replica_nodes(nodes):
            replicate_nodes = []
            # Format nodes for Ring Builder
            for node in nodes:
                replicate_nodes.append((node['weight'],
                                       node['node_slot'],))
            return replicate_nodes

        # Count Zones with Nodes
        zones2nodes = self.zones2nodes
        zone_count = len(zones2nodes)
        zones_over = max(zone_count - (1 + self._replicas), 0)

        replica2nodes = []

        # Replicas for Ring if Zones are Equal to Replicas
        for scan in range(max(1 + self._replicas, zone_count)):
            zone = scan % zone_count
            replica = scan % (1 + self._replicas)
            if len(replica2nodes) < replica + 1:
                replica2nodes.append([])
            if replica > zone:
                # Perform this when more replica than zones.
                # Copies last replica in order to next replica.
                # Every duplicate replica also has its nodes reversed.
                copy_replica = len(replica2nodes) - 1 - zone_count
                replica2nodes[replica] = list(reversed(
                    replica2nodes[copy_replica]))
            else:
                # Perform this when more zones than replicas.
                # Adds next zone of nodes in order from first replica.
                if zone >= zone_count - zones_over:
                    replica = zone % (1 + self._replicas)
                    replica2nodes[replica] += format_replica_nodes(
                        zones2nodes[zone])
                else:
                    # Perform this under normal cirumstances.
                    # When replicas and zones are equal at the time.
                    replica2nodes[replica] += format_replica_nodes(
                        zones2nodes[zone])

        return replica2nodes

    def __len__(self):
        return len(self._node_index)

    def test_create_nodes(self, nodes=1, zone=1):
        """Create Test node entries.

        Args:
            nodes (int): Number of Nodes to create.
            zone (int): zone to create or add nodes to.
        """
        zone = "Zone-%s" % zone
        try:
            self.add_zone(zone)
        except DuplicateError:
            pass

        for node in range(nodes):
            self.add_node(zone=zone, weight=1)


class Ring(object):
    """Ring

    Ring is used to build a consistent hashing ring and manage through out its
    life span. Its important the nodes are added in specific exact same order
    to ensure minimal changes to the ring. For speed and consistancy a ring
    should be saved and loaded from previous ring.

    The Ring provides the ability to:
        * Snapshots to ensure previous known slot locations are availible.
        * Get Nodes for specific hashed data_id.
        * Ability to check if slot location has changed for node.
        * Provide remote replicas for Node slots.
        * Versioning of Ring on adding of nodes or build/rebalance.

    When rebuilding/rebalancing the Ring using the build method a snapshot is
    created. (Only 4 snapshots are kept) An Object store could use snapshots
    to try locate a missing or moved object by iterating the snapshots. The
    more snapshots you need to iterate to find slot containing object in object
    store the slower the lookup will be. Ensure you make all changes required
    for rebuilding/rebalancing the ring. If you need to add 3 nodes for
    example, ensure you add all of them at once before rebuilding/rebalancing.

    Versioning could be used to determine if the Ring is upto date with other
    endpoints using the Ring. All endpoints should have same copy of the ring.
    Endpoints being nodes/devices that contain distribute load of objects for
    example.

    The ring has some test methods to validate and test the algorithems.

    Each node can be assigned to a zone. Zones are preferred for replica
    copies. If more replicas exist than zones, then some zones will be re-used
    for repica copies.

    Its recommended to ensure equal amount of zones than duplicate copies. For
    example using replicas 2 then 3 zones should be used.

    Altering the replicas and zones will increase the amount of slots being
    re-assigned. In an object store this means more data will be moved around
    during a reblance/rebuild. This functionality is not allowed.

    The ring_power determiens the size of each replica ring. A ring_power of 16
    bits is used by default. This ensures each ring has 65535 slots. Using this
    ring_power ensures if 4096 nodes in replica have equal weight, they can
    occupy 16 slots each. Its not recommended to have more than 4096 nodes in a
    zone using 16bit Ring Size.

    Args:
        nodes (NodesTree): NodesTree Object.

    Keyword Args:
        ring_path (str/bytes): Load exisiting ring from pickle file.
        ring_power (int): Bits for size of ring. (should never change)
        replicas (int): Duplicate nodes to distribute.
    """
    TEST_COUNT = 1000000
    MAX_SNAPSHOTS = 4

    def __init__(self, nodes, ring_path=None, ring_power=22, replicas=2):
        if ring_path:
            ring = load(ring_path, 644)
            self._snapshots = ring['snapshots']
            self._ring_power = ring['ring_power']
            self._replicas = ring['replicas']
            self._version = ring['version']
        else:
            self._snapshots = []
            self._ring_power = ring_power
            self._replicas = replicas
            self._version = 0

        self._nodes = nodes

    def save(self, ring_path):
        """Save ring to pickle file.

        Args:
            ring_path (str): Path to ring pickle file.
        """
        ring = {}
        ring['snapshots'] = self._snapshots
        ring['ring_power'] = self._ring_power
        ring['replicas'] = self._replicas
        ring['version'] = self._version

        save(ring, ring_path, 644)

    @property
    def power(self):
        return self._ring_power

    @property
    def slots(self):
        return (2 ** self._ring_power)

    @property
    def replicas(self):
        return self._replicas

    @property
    def version(self):
        """Return version.
        """
        return self._version

    def get(self, data_id, duplicate=False):
        """Get nodes by consistant hash.

        Args:
            data_id (int,str):  Unique id to hash to slot.
            duplicate (bool): Remove Duplicate nodes in older snapshots.
                              (dafault: False)

        Returns:
            tuple: Snapshots with value of replica nodes in tuple.
        """
        slot = get_slot(self._ring_power, data_id)

        return self.get_ring_slot(slot, duplicate=duplicate)

    def get_ring_slot(self, slot, duplicate=False):
        """Get nodes by slot for composite ring.

        Args:
            slot (int): Ring slot number.
            duplicate (bool): Remove duplicate nodes in older snapshots.
                              (dafault: False)

        Returns:
            tuple: Snapshots with value of replica nodes in tuple.
        """
        if not self._snapshots:
            raise ValueError('Ring not built')

        duplicates = []
        snapshots = []
        for snapshot in self._snapshots:
            nodes = []
            for replica_no, replica in enumerate(snapshot):
                replica_node = replica[slot]
                dup = "%s-%s" % (replica_node, replica_no,)
                if dup not in duplicates or duplicate is True:
                    duplicates.append(dup)
                    node = self._nodes.get_node(replica[slot])
                    if node:
                        extra = {"composite_slot": slot + (replica_no *
                                                           self.slots),
                                 "ring_slot": slot,
                                 "ring_replica": replica_no}
                        nodes.append({**node, **extra})
            if nodes:
                snapshots.append(tuple(nodes))

        return tuple(snapshots)

    def get_composite_slot(self, slot, duplicate=False):
        """Gets nodes by composite slot in ring.

        Args:
            slot (int): Ring slot number.
            duplicate (bool): Remove duplicate nodes in older snapshots.
                              (dafault: False)

        Returns:
            tuple: Snapshots with value of replica nodes in tuple.
        """
        if not self._snapshots:
            raise ValueError('Ring not built')

        replica_no = math.floor(slot / self.slots) % (1 + self.replicas)
        slot = slot % self.slots

        duplicates = []
        snapshots = []

        for snapshot in self._snapshots:
            replica_node = snapshot[replica_no][slot]
            dup = "%s-%s" % (replica_node, replica_no,)
            if dup not in duplicates or duplicate is True:
                duplicates.append(dup)
                node = self._nodes.get_node(replica_node)
                if node:
                    extra = {"composite_slot": slot + (replica_no *
                                                       self.slots),
                             "ring_slot": slot,
                             "ring_replica": replica_no}
                    snapshots.append({**node, **extra})

        return tuple(snapshots)

    def build(self):
        """Build/Rebalance ring.

        Build composite Ring, which consists of 'replica' rings.
        """
        log.info("Building Ring: Replicas '%s' Zones '%s' Nodes '%s' " %
                 (self._replicas,
                  len(self._nodes.zones),
                  len(self._nodes),) +
                 "Ring Power '%sBits' Slots Per Replica '%s'" %
                 (self._ring_power,
                  2 ** self._ring_power,))

        nodes = self._nodes.build_replicates()

        replicas = []

        for replica in range(1 + self._replicas):
            slot2node = build_ring(nodes[replica],
                                   self._ring_power,
                                   replica)
            if slot2node:
                replicas.append(slot2node)

        self._snapshots.insert(0, replicas)
        self._version += 1

        if len(self._snapshots) == Ring.MAX_SNAPSHOTS:
            del self._snapshots[Ring.MAX_SNAPSHOTS:]

        log.info("Completed Building Nodes into Replicas")

    def test_distribution(self):
        """Test Distribution.

        Test distirbution of objects between nodes and zones.

        Returns:
            tuple: (nodes, zones)
        """
        def analyse(data, name):
            results = []
            for key in data:
                dist = (100 * float(data[key])/float(Ring.TEST_COUNT))
                results.append({name: key, 'dist': data[key], 'percent': dist})
            results = sorted(results, key=lambda k: k['percent'], reverse=True)
            for result in results:
                print("%s: '%s', Distributed '%s' %s%s" % (name,
                                                           result[name],
                                                           result['dist'],
                                                           result['percent'],
                                                           '%',))
            return results

        node_counts = {}
        zone_counts = {}
        for zone in self._nodes.zones:
            node_counts[zone[0]] = {}
        for data_id in range(Ring.TEST_COUNT):
            for node in self.get(data_id)[0]:
                node_counts[node['zone']][node['node_id']] = \
                    node_counts[node['zone']].get(node['node_id'], 0) + 1
                zone_counts[node['zone']] = \
                    zone_counts.get(node['zone'], 0) + 1

        for zone in node_counts:
            print("Zone: %s Total Nodes: %s" % (zone, len(node_counts[zone]),))
            print("----------------------")
            nodes = analyse(node_counts[zone], 'node_id')

        print("Zone Distribution")
        print("----------------------")
        zones = analyse(zone_counts, 'zone_id')

        return (nodes, zones,)

    def test_compare(self):
        """Test snapshot comparison.

        When two or more snapshots are created this function is used to
        determine how many objects have moved. The simulation is is based on a
        small amunt of of data_id(s) and therefor expected no have perfect
        results.

        iterations_to_match: Iterations needed to match a original node.
        moved_objects: Moved objects.
        percent_moved: Percent moved.
        object_found_first: Object found first.
        object_found_first_percent: Object found first found percent.

        Returns:
            tuple: (iterations to match, moved_objects, percent_moved,
                    object_found_first, object_found_first_percent)
        """
        moved_objects = 0
        not_moved_objects = 0
        first_found_objects = 0
        iterations_to_match = []
        for data_id in range(Ring.TEST_COUNT):
            found_moved = []
            found_first = []
            snapshots = self.get(data_id, duplicate=True)
            # Scan for moved, first found objects.
            for snapshot_no, replica in enumerate(snapshots):
                for node_no, node in enumerate(replica):
                    node_id = "%s-%s-%s" % (node['node_id'],
                                            node['ring_slot'],
                                            node['ring_replica'],)
                    if snapshot_no > 0:
                        if node_id not in found_moved[node_no]:
                            moved_objects += 1
                        else:
                            not_moved_objects += 1
                    else:
                        found_first.append(node_id)
                        found_moved.append(node_id)

                    if len(snapshots) - 1 == snapshot_no:
                        if node_id in found_first[node_no]:
                            iterations_to_match.append(node_no)
                            if node_no == 0:
                                first_found_objects += 1
                        else:
                            iterations_to_match.append(
                                snapshot_no + len(replica))

        iterations_to_match = round(sum(
            iterations_to_match)/len(iterations_to_match), 2)
        total_objects = (1 + self._replicas) * Ring.TEST_COUNT
        first_found_objects = max(first_found_objects, 0)
        moved_objects = math.ceil(moved_objects / (1 + self._replicas))
        percent_moved = round(100 *
                              (float(moved_objects)/float(total_objects)), 2)
        percent_first_found = \
            round(100 * (float(first_found_objects)/float(Ring.TEST_COUNT)), 2)

        print("For match:\n" + "=" * 60)
        print("Average Max Iterations: %s" %
              (iterations_to_match, ))
        print("Objects Moved: %s/%s (%s%s)" %
              (moved_objects,
               total_objects,
               percent_moved, '%',))
        print("Found Objects: %s/%s (%s%s)" %
              (first_found_objects,
               Ring.TEST_COUNT,
               percent_first_found, '%',))

        return (iterations_to_match, moved_objects, percent_moved,
                first_found_objects, percent_first_found,)
