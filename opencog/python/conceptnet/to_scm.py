__author__ = 'Amen Belayneh'

# This code creates a scheme file, after inputing the address to a conceptnet
#  csv file dump. The conceptnet csv file should be in the same folder as this
# script. Make sure you add '.scm' when inputting the name for the scheme
# output file. The output file will be in the same folder as the script

from opencog.atomspace import TruthValue, types, get_type, AtomSpace
import reader
import term
import sys
import math

corpus_path = ""
corpus_dict = {}
conceptnet_dict = {}
twf = 0


# ConceptNet relation to Opencog Link mappings
def map(relation, dict):
    if dict == 1:
        map_dict1 = {
            "/r/ConceptuallyRelatedTo": "IntensionalSimilarityLink",
            "/r/ThematicKLine": "IntensionalSimilarityLink",
            "/r/SuperThematicKLine": "IntensionalInheritanceLink",
            "/r/IsA": "InheritanceLink",
            "/r/PropertyOf": "InheritanceLink",
            "/r/DefinedAs": "SimilarityLink",
            "/r/PrerequisiteEventOf": "RetroactiveImplicationLink",
            "/r/FirstSubeventOf": "StartsLink",
            "/r/SubeventOf": "DuringLink",
            "/r/LastSubeventOf": "EndsLink",
            "/r/EffectOf": "PredictiveImplicationLink",
            "/r/HasPrerequisite": "RetroactiveImplicationLink",
            "/r/Causes": "PredictiveImplicationLink",
            "/r/HasProperty": "IntensionalInheritanceLink",
            "/r/HasSubevent": "DuringLink"
        }
        try:
            if map_dict1[relation] in types.__dict__.keys():
                return map_dict1[relation]
            else:
                return "EvaluationLink"
        except KeyError:
            return "EvaluationLink"
    elif dict == 2:
        try:
            map_dict2 = {"/r/EffectOf": "EvaluationLink"}
            return map_dict2[relation]
        except KeyError:
            return False


def set_TV(word):
    global corpus_dict, conceptnet_dict, twf
    if not(corpus_dict):
        term_lists = term.read_frequencies(corpus_path)
        corpus_dict = dict(term_lists)
        twf = term.total_freq(term_lists)

    try:
        stv = conceptnet_dict[word]
        return stv
    except KeyError:
        if ("  " + word.upper()) in corpus_dict:
            mean = float(corpus_dict[("  " + word.upper())]) / twf
            count = .95  # have no reason for this value
            conceptnet_dict[word] = TruthValue(mean, count)
            return conceptnet_dict[word]
        else:
            mean = 1 / (twf + 1)
            count = .95  # have no reason for this value
            conceptnet_dict[word] = TruthValue(mean, count)
            return conceptnet_dict[word]


def write_atoms(atomspace, cn_assertion, template_no, link_type=''):

    cn_argument1=cn_assertion[1][6:]
    cn_argument2=cn_assertion[2][6:]
    cn_arg1_stv=set_TV(cn_argument1)
    cn_arg2_stv=set_TV(cn_argument2)
    cn_confidence=float(cn_assertion[4])
    if(cn_confidence > 0.0):
        # For true statements we give a strength of 0.5 to 1.0, ramping up
        # quickly towards 1.0 as the cn_confidence grows.
        confidence_value = 1.0 - math.pow(0.2, cn_confidence)/2.0
    else:
        # For any false statement we currently just set a strength of 0.0, basically
        # ignoring the conceptnet confidence value other than to note that it was false.
        #TODO: This could probably be improved, but not sure how.
        confidence_value = 0.0

    # For the STV we use the computed confidence from conceptnet as the 'strength'.
    # Currently just using a 'confidence' of ~0.9 indicating that whatever
    # conceptnet thinks the truth value is, we agree strongly with this
    # analysis.  Maybe something better could be done, hard to say for sure
    # though.  The 10000 gets converted to the confidence of ~0.9 by the constructor.
    TV = TruthValue(confidence_value, 10000)

    cn1 = atomspace.add_node(types.ConceptNode, cn_argument1, tv=cn_arg1_stv)
    cn2 = atomspace.add_node(types.ConceptNode, cn_argument2, tv=cn_arg2_stv)

    if template_no == 1:
        link = atomspace.add_link(get_type(link_type), [cn1, cn2], tv=TV)

        return repr(link)
    elif template_no == 2:
        cn_relation=cn_assertion[0][3:]
        pn = atomspace.add_node(types.PredicateNode, cn_relation, tv=TV)

        listlink = atomspace.add_link(types.ListLink, [cn1, cn2])
        evallink = atomspace.add_link(types.EvaluationLink, [pn, listlink], tv=TV)
        return repr(evallink)

def from_file(atomspace, cn_path, scm_name):
    # lists_of_assertions is a list of list of assertion
    print "Reading input csv file..."
    lists_of_assertions = reader.csv(cn_path)
    print "\n\nReading complete, beginning processing..."
    with open(scm_name, 'w') as scm_file:
        for an_assertion in lists_of_assertions:
            sentence = an_assertion[5].replace('[', '').replace(']', '').replace('\'', '\\\'')
            if len(sentence) > 0:
                scm_file.write("(r2l '" + sentence + "')" + "\n" * 2)

            if map(an_assertion[0], 2):
                temp = write_atoms(atomspace, an_assertion, 2)
                scm_file.write(temp + '\n' * 2)

            if ((map(an_assertion[0], 1) == "EvaluationLink") and
            (map(an_assertion[0], 2) != "EvaluationLink")):
                # this condition is to prevent repetition of EvaluationLink
                temp = write_atoms(atomspace, an_assertion, 2)
            elif map(an_assertion[0], 1) != "EvaluationLink":
                temp = write_atoms(atomspace, an_assertion, 1, map(an_assertion[0], 1))
            scm_file.write(temp + '\n' * 2)

if __name__ == '__main__':
    # If the script was called with no command line arguments
    if len(sys.argv) == 1:
        cn_url = raw_input("Enter ConceptNet csv file address: ")
        corpus_path = raw_input("Enter corpus address: ")
        name_of_scm_file = raw_input("Enter name for the Scheme Output file: ")
    elif len(sys.argv) == 4:
        cn_url = sys.argv[1]
        corpus_path = sys.argv[2]
        name_of_scm_file = sys.argv[3]
    else:
        print "\n\n\tUsage: " + sys.argv[0] + " input.csv corpus_freqs.csv outputfile.scm\n\n"
        sys.exit(1)

    atomspace = AtomSpace()
    from_file(atomspace, cn_url, name_of_scm_file)
    print ("Scheme file is created successfully")
