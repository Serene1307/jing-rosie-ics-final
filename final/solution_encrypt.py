import random
random.seed(0)

# implement this
def read_file(file_name):
    msg_list = [""]
    # -------- start of your code -------- #
    pass

    # solution:
    try:
        msg_list = open(file_name, "r").readlines()
    except FileNotFoundError:
        print("%s not found!" % file_name)
    # -------- end of your code --------#

    return msg_list
"""
The following function encodes a character according to a given offset
DO NOT EDIT THIS FUNCTION
Note:
ord() gives the ASCII code of the character.
   Eg: ord(‘a’) is 97

chr() gives the corresponding character for given ASCII code.
    Eg: chr(97) is ‘a’
"""

def encrypt_a_letter(c, offset):
    if c.islower():
        if ord(c) + offset <= ord('z'):
            return chr( ord(c) + offset )
        else:
            return chr( ord(c) + offset - 26 )
    elif c.isupper():
        if ord(c) + offset <= ord('Z'):
            return chr( ord(c) + offset )
        else:
            return chr( ord(c) + offset - 26 )
    else:
        return c

"""
The following function selects a random message, enctryp it with a random offset
# DO NOT EDIT THIS
"""
def generate_encrypted_msg(offset, msg):
    
    encrypted_msg = ""
    for c in msg:
        encrypted_msg += encrypt_a_letter(c,offset)
    return encrypted_msg


# This essentially is the inverse of the given encrypt_a_letter() function
# implement this
def decrypt_a_letter(c, offset):

    # -------- start of your code -------- #
    pass

    # solution:
    if c.islower():
        if ord(c) - offset >= ord('a'):
            return chr( ord(c) - offset )
        else:
            return chr( ord(c) - offset + 26 )
    elif c.isupper():
        if ord(c) - offset >= ord('A'):
            return chr( ord(c) - offset )
        else:
            return chr( ord(c) - offset + 26 )
    else:
        return c
    # -------- end of your code --------#
    return c

# =============================================================================
# print(decrypt_a_letter('a', 1))
# print(decrypt_a_letter('a', 25))
# =============================================================================

def decrypt_msg(offset, msg):
    """
    Use any approach you deem fit to solve the problem.
    Brute force (IE, trying every offset & seeing if you get a match) is a good
    first approach.
    You are encouraged to write any additional function(s) you may need
    """
    # -------- start of your code -------- #
    pass

    # solution:
    decrypted_msg = ""
    for c in msg:
        decrypted_msg += decrypt_a_letter(c,offset)
    return decrypted_msg

    
    # -------- end of your code --------#
  

# =============================================================================
# print(decrypt_msg('am', ['c', 'am']))
# print(decrypt_msg('bn', ['ck', 'am', 'hello']))
# =============================================================================



# Main code - DO NOT EDIT THIS
if __name__ == "__main__":

    file_name = "messagelist.txt"
    msg_list = read_file(file_name)

    encrypted_msg = generate_encrypted_msg(msg_list)
    print("Your encrypted message is:\n" + encrypted_msg)

    decrypted_msg, offset = decrypt_msg(encrypted_msg, msg_list)
    print("The decrypted message is:\n" + decrypted_msg)

    print("The substitution offset =", offset)
