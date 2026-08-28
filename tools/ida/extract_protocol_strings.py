"""Extract NESYS and TCP protocol specific strings."""
import json


def main():
    with open(r'C:\Users\KAHO\Pictures\Starwing\tools\ida\string_analysis_results.json', 'r') as f:
        data = json.load(f)
    
    shipping = data['AcrGame-Win64-Shipping.exe']['filtered_matches']
    
    print("=== NESYS Protocol Strings ===\n")
    nesys_strings = shipping.get('nesys', [])
    for s in nesys_strings[:50]:
        print(f"  {s['value']}")
    
    print("\n=== TCP Protocol Strings ===\n")
    tcp_strings = shipping.get('tcp', [])
    for s in tcp_strings[:50]:
        print(f"  {s['value']}")
    
    print("\n=== Matching Protocol Strings ===\n")
    matching_strings = shipping.get('matching', [])
    for s in matching_strings[:50]:
        print(f"  {s['value']}")
    
    print("\n=== Session Strings ===\n")
    session_strings = shipping.get('session', [])
    for s in session_strings[:30]:
        print(f"  {s['value']}")
    
    print("\n=== Card Strings ===\n")
    card_strings = shipping.get('card', [])
    for s in card_strings[:30]:
        print(f"  {s['value']}")
    
    print("\n=== Heartbeat Strings ===\n")
    heartbeat_strings = shipping.get('heartbeat', [])
    for s in heartbeat_strings:
        print(f"  {s['value']}")
    
    print("\n=== Timeout Strings ===\n")
    timeout_strings = shipping.get('timeout', [])
    for s in timeout_strings[:20]:
        print(f"  {s['value']}")
    
    print("\n=== Reconnect Strings ===\n")
    reconnect_strings = shipping.get('reconnect', [])
    for s in reconnect_strings:
        print(f"  {s['value']}")
    
    print("\n=== GameServer Strings ===\n")
    gameserver_strings = shipping.get('GameServer', [])
    for s in gameserver_strings[:30]:
        print(f"  {s['value']}")
    
    print("\n=== Starwing URLs ===\n")
    starwing_strings = shipping.get('starwing', [])
    for s in starwing_strings:
        print(f"  {s['value']}")
    
    print("\n=== GALAXYIO DLL Strings ===\n")
    galaxyio = data['GALAXYIO.dll']['filtered_matches']
    
    print("HTTP-related:")
    http_strings = galaxyio.get('http', [])
    for s in http_strings:
        print(f"  {s['value']}")
    
    print("\nCard-related:")
    card_strings = galaxyio.get('card', [])
    for s in card_strings:
        print(f"  {s['value']}")
    
    print("\nNESYS-related:")
    nesys_strings = galaxyio.get('nesys', [])
    for s in nesys_strings:
        print(f"  {s['value']}")
    
    print("\nGalaxy-related:")
    galaxy_strings = galaxyio.get('galaxy', [])
    for s in galaxy_strings:
        print(f"  {s['value']}")


if __name__ == "__main__":
    main()
