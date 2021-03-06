import argparse
import os
from Bio import SeqIO
from Bio import pairwise2
import re
from csv import writer


def parseFastaFile(fn, returnAs = "dict"):
  if returnAs == "dict":
    seqs = {}
  elif returnAs == "list":
    seqs = []

  for record in SeqIO.parse(fn, format = "fasta"):
    if returnAs == "dict":
      seqs[record.id] = record.seq
    elif returnAs == "list":
      seqs.append(record)

  return seqs


def getAllNaFaFiles(dir):
  extOfInterest = ".na.fasta"
  fns = [fn for fn in os.listdir(dir) if fn.endswith(extOfInterest)]

  return(fns)


def parseNaFaRecord(rec, subjDict, regionName):
  if "HXB2" in rec.id:
    return None
  
  cleanSeq = rec.seq.ungap("-")
  if len(cleanSeq) < 15:
    return None

  subjKey = rec.id.replace("_" + regionName, "")

  # splicing aware detection
  if regionName in ["Rev", "Tat"]:
    alns = pairwise2.align.localmd(subjDict[subjKey], cleanSeq, 3, -3, -100, -100, -5, 0)

    if len(alns) != 1:
      return None

    seqBGapped = alns[0].seqB
    matches = re.finditer(r"([^-]+)", seqBGapped)
    matchesCondensed = [[x.start(), x.end()] for x in matches]
    
    returnObj = []
    for y in matchesCondensed:
      returnObj.append({
        "subj": subjKey,
        "hivRegion": regionName,
        "subjStart": y[0],
        "subjEnd": y[1] - 1        
      })

  else:
    coordinateMatch = [match for match in re.finditer(str(cleanSeq), str(subjDict[subjKey]))]
    if len(coordinateMatch) == 0:
      return None

    elif len(coordinateMatch) > 2:
      print("More than one pattern found for: {}".format(rec.id))
      return None

    elif len(coordinateMatch) == 2:
      if regionName == "3LTR" and coordinateMatch[1].start() > coordinateMatch[0].start():
        coordinateMatch = [coordinateMatch[1]]
      elif regionName == "5LTR" and coordinateMatch[0].start() < coordinateMatch[1].start():
        coordinateMatch = [coordinateMatch[0]]
      else:
        print("Subject sequence likely reversed for: {}".format(rec.id))

    # return as 0 index
    returnObj = {
      "subj": subjKey,
      "hivRegion": regionName,
      "subjStart": coordinateMatch[0].start(),
      "subjEnd": coordinateMatch[0].end() - 1
    }

  return returnObj


def parseNaFaFiles(fns, parentDir, subjDict):
  finalResults = []

  for fn in fns:
    regionName = fn.replace(".na.fasta", "")
    fullFn = parentDir + "/" + fn

    records = parseFastaFile(fullFn, returnAs = "list")
    for r in records:
      res = parseNaFaRecord(r, subjDict, regionName)
      if res is not None:
        if type(res) == list:
          for x in res:
            finalResults.append(x)
        else:  
          finalResults.append(res)

  return finalResults


def exportResults(results, fn):
  with open(fn, "w") as tsvfile:
    writ = writer(tsvfile, delimiter = "\t")

    writ.writerow(["annotation", "startPos", "endPos", "genome"])
  
    for r in results:
      writ.writerow([r["hivRegion"], r["subjStart"], r["subjEnd"], r["subj"]])


def main(args):
  subjSeqs = parseFastaFile(args.subjectSequences, returnAs = "dict")
  geneCutterFiles = getAllNaFaFiles(args.geneCutterResults)
  results = parseNaFaFiles(geneCutterFiles, args.geneCutterResults, subjSeqs)

  exportResults(results, args.outputDir + "/GeneCutterParser_" + args.runID + ".tsv")


if __name__ == '__main__':
  # set up command line arguments
  parser = argparse.ArgumentParser(
    description = "Parse HIV LANL Database Gene Cutter results")

  parser.add_argument(
    "--subjectSequences",
    required = True,
    type = os.path.abspath,
    help = "Fasta file. HIV sequences used for input into Gene Cutter. Fasta record names must match original input.")
  
  parser.add_argument(
    "--runID",
    required = True,
    help = "Run ID")

  parser.add_argument(
    "--geneCutterResults",
    required = True,
    type = os.path.abspath,
    help = "Directory containing Gene Cutter Results (should be multiple .na.fa files present).")

  parser.add_argument(
    "--outputDir",
    type = os.path.abspath,
    default = os.path.abspath("."),
    help = "Output folder")

  args = parser.parse_args()
  
  if not os.path.exists(args.outputDir):
    os.makedirs(args.outputDir)

  if not os.path.exists(args.subjectSequences):
    raise Exception("Fasta file not found")

  if not os.path.exists(args.geneCutterResults):
    raise Exception("Gene Cutter folder doesn't exist")

  main(args)