
import re
import sys


def ParsePatch(filename):
  lines = [line.rstrip('\n') for line in open(filename, 'r')]

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

  hunks = []
  i = 0
  while i < len(lines):
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
      hunks.append((rem, add))
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
  patch1 = ParsePatch(patch_file1)
  patch2 = ParsePatch(patch_file2)

  def Put(patch, dest_file):
    fh = open(dest_file, 'w')
    fh.write('%i patches\n' % len(patch))
    for hunk in patch:
      fh.write('\nPatch:\n')
      WriteHunk(fh, hunk)
    fh.close()

  Put(list(Diff(patch1, patch2)), 'out-before')
  Put(list(Diff(patch2, patch1)), 'out-after')


if __name__ == '__main__':
  Main(sys.argv[1:])
