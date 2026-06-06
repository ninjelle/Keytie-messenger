from network import Messenger

alice = Messenger("alice")
bob = Messenger("bob")

alice.register()
bob.register()

alice.send("bob", "Privet, Bob, cherez server!")
print("Bob:", bob.receive())

bob.send("alice", "Privet, Alice! Poluchil.")
print("Alice:", alice.receive())