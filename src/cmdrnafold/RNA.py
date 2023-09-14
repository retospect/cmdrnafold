import asyncio


class RNArunner:
    def __init__(self, sequence):
        cmd = "RNAFold --noPS"
        self.sequence = sequence
        self.cmd = cmd
        self.hash = hash(cmd + sequence)
        self.proc = asyncio.create_subprocess_shell(
            cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        control = sequence + "\n@\n"
        self.proc.stdin.write(control.encode())

    def mfe(self):
        # Read the result
        result = self.proc.stdout.read()
        # Extract the structure and the mfe number
        result = result.split("\n")
        structure = result[7]
        mfeStr = result[8]
        # get the number from the string: " minimum free energy =  -9.80 kcal/mol"
        mfe = float(mfeStr.split(" ")[-2])
        return (structure, mfe)

    def __hash__(self):
        return self.hash


def fold_compound(sequence):
    # Make a new instance of RNArunner
    return RNArunner(sequence)
