# Starsector-Java-Mappings
Java Mappings for [Starsector](https://fractalsoftworks.com/).

Contains Mappings for Starsector obfuscated JARs to something that's humanly readable.


> [!IMPORTANT]  
> Currently, only the Linux version of teh game is being mapped. So to view mapped code you must download the Linux version of the game and go from there (no need to launch it or anything, just get those JARs).

> [!WARNING]  
> This is a **VERY** early work-in-progress project and by no means done by a professional (I'm pretty novice at Java, obfuscation technics and modding).


### Mapping status

| JAR                 | Progress |
|---------------------|----------|
| `starfarer_obj.jar` | Minimal  |
| `fs.common_obf.jar` | Minimal  |
|                     |          |


## About

The main JAR that contains game-related code is `starfarer_obf.jar`. `starfarer.api.jar` is the unobfuscated version of that jar containing limited subset of code. The project aims to map out the obfuscated JARs (`starfarer_obf.jar` and any other game JAR) for modding purposes.

The JAR files differ between game versions AND platforms. Currently, only the Linux version of the game is being mapped (but it can be viewed regardless of your platform - see the notice at the start of this README).

1. The mappings are first generated using [Recaf](https://github.com/Col-E/Recaf) and its "illegal name cleanup" feature to get rid of random unicode and super long `OOOOOOOOOOOOOOOOOOOO`-like names to something less hideous to look at (e.g: `method1364`, `field8381`, etc.).
2. The mappings then loaded into [Enigma](https://github.com/FabricMC/Enigma) (a deubfuscator and remapper used for Minecraft modding) and manually constructed by "looking through the code and seeing what it does".
3. The mapping can then be applied by *<TODO: figure out this part>.*

## Project structure

All mappings are located in `mappings` folder, divided into game versions. Mappings span all JARs for that game version. The mapping file is named `__ALL__.mapping` - it contains mappings for all game JARs at the same time.

"Clean" mappings with no illegal names produced by Recaf are stored in `__ALL__no_illegals.mapping`.

## Mapping & mapping conventions

- Mappings I'm sure about are named normally.
- Mappings I'm unsure about end with `Rrr`.
- Mappings created with use of AI (don't shame me try to map those math methods yourself!) end with `Rai`. Javadoc written by AI start with "AI:".
- Mappings produced by Recaf's "illegal name resolution" are stored under `mapped` mapping project. They have generic names like  `method1364`, `field8381`, etc. They are eventually moved into the main space.

**Other cases:**
- Methods that only call the same method with same args and do nothing else are suffixed with `__COPY`. Not sure if those are the results from obfuscation or if they exist in the original code.

## Applying mappings

### Enigma
https://github.com/FabricMC/Enigma

To apply mappings in Enigma, first open the relevant JAR file.

Then use File > Open Mappings... > Enigma File and choose the relevant `.mapping` file.

To save mappings, use File > Save Mappings.

### Recaf GUI
https://github.com/Col-E/Recaf

To apply mappings in Recaf, first open the relevant JAR file.

Then use Mappings > Apply > Enigma and pick the `.mapping` file. If you are getting errors, try opening the mappings in Enigma and running File > Drop Invalid Mappings.

To save mappings, use Mappings > Export > Enigma.

### Game files

If only I knew... please contact me or make a pull request explaining how to do this!

## Contributing

PRs are welcome, although I'm unsure how well the mappings will merge. A some sort of merging feature is probably required for this to work... Enigma also has a collaboration feature. If you are willing, contact me or make an issue to figure this out!

## FAQ

### Enigma

#### Some methods show up named "new" instead of a legal name

Try temporarily switching decompiler to Procyon (Decompiler > Procyon).

### Recaf

#### Error while loading Enigma mappings

In Enigma, try File > Drop Invalid Mappings.