
import re
import sys


def MergeFilenames(filename1, filename2):
  names = set()
  if filename1 != '/dev/null':
    assert filename1.startswith('a/')
    names.add(filename1[2:])
  if filename2 != '/dev/null':
    assert filename2.startswith('b/')
    names.add(filename2[2:])
  assert len(names) == 1
  return list(names)[0]


# Remove empty lines at the start and end of the patch, because they
# are usually not important and are just the result of changes in
# context.
def CleanWhitespace(lines):
  lines = list(lines)
  while len(lines) > 0 and lines[0].strip() == '':
    lines.pop(0)
  while len(lines) > 0 and lines[-1].strip() == '':
    lines.pop(-1)
  return tuple(lines)


def ParsePatch(patch_file):
  lines = [line.rstrip('\n') for line in open(patch_file, 'r')]

  def MatchChar(char):
    def M(line):
      if line.startswith(char):
        return line[1:]
      return None
    return M

  def Matches(i, func):
    got = []
    while i < len(lines):
      m = func(lines[i])
      if m is None:
        break
      got.append(m)
      i += 1
    return tuple(got), i

  filename = None
  hunks = []
  i = 0
  while i < len(lines):
    m = re.match('--- (.*)', lines[i])
    if m:
      filename1 = m.group(1)
      m = re.match('\+\+\+ (.*)', lines[i + 1])
      filename2 = m.group(1)
      filename = MergeFilenames(filename1, filename2)
      i += 2
    if not lines[i].startswith('@@'):
      i += 1
      continue
    i += 1
    while True:
      ctx, i = Matches(i, MatchChar(' '))
      rem, i = Matches(i, MatchChar('-'))
      add, i = Matches(i, MatchChar('+'))
      if len(rem) == 0 and len(add) == 0:
        break
      hunks.append((filename, (CleanWhitespace(rem), CleanWhitespace(add))))
  return hunks


def WriteHunk(fh, hunk):
  rem, add = hunk
  for line in rem:
    fh.write('-%s\n' % line)
  for line in add:
    fh.write('+%s\n' % line)


def Diff(list1, list2):
  set2 = set(list2)
  for item in list1:
    if item not in set2:
      yield item


def Main(args):
  patch_file1 = args[0]
  patch_file2 = args[1]
  patch_orig1 = ParsePatch(patch_file1)
  patch_orig2 = ParsePatch(patch_file2)
  patch1 = list(Diff(patch_orig1, patch_orig2))
  patch2 = list(Diff(patch_orig2, patch_orig1))

  def Put(patch, dest_file):
    fh = open(dest_file, 'w')
    fh.write('%i patches\n' % len(patch))

    by_filename = {}
    for filename, hunk in patch:
      by_filename.setdefault(filename, []).append(hunk)

    fh.write('\nSummary of files:\n')
    for filename in sorted(by_filename.iterkeys()):
      fh.write('  %s\n' % filename)

    for filename, hunks in sorted(by_filename.iteritems()):
      fh.write('\nFile %s:\n' % filename)
      for hunk in hunks:
        fh.write('\nPatch:\n')
        WriteHunk(fh, hunk)
    fh.close()

  Put(patch1, 'out-before')
  Put(patch2, 'out-after')


if __name__ == '__main__':
  Main(sys.argv[1:])
