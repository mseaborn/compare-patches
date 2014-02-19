
import subprocess
import sys

import compare_patches


def Main(args):
  assert len(args) == 1
  merge_commit = args[0]
  merge_commit = subprocess.check_output(['git', 'rev-parse',
                                          merge_commit]).strip()
  parents = subprocess.check_output(
    ['git', 'log', '--no-walk', '--pretty=format:%P',
     merge_commit])
  parents = parents.strip().split()
  assert len(parents) == 2

  base = subprocess.check_output(['git', 'merge-base'] + parents).strip()

  top_banner = 'Examining merge commit %s\n%s\n\n' % (
      merge_commit,
      subprocess.check_output(['git', 'log', '--no-walk',
                               '--pretty=format:("%s", %cd)', merge_commit]))

  def Diff(this_side, other_side, commits):
    banner = top_banner
    banner += '%s the merge:\n\n' % this_side.capitalize()
    cmd = ['git', 'diff'] + commits

    fh = open('tmp_%s.patch' % this_side, 'w')
    fh.write(banner)
    fh.flush()
    subprocess.check_call(cmd, stdout=fh)

    banner += ('These are the patch hunks from %s the merge '
               'that do not also appear %s.\n\n' % (this_side, other_side))
    banner += 'These patch hunks come from:\n%s\n\n' % ' '.join(cmd)
    return banner

  banner1 = Diff('before', 'after', [base, parents[0]])
  banner2 = Diff('after', 'before', [parents[1], merge_commit])
  compare_patches.ComparePatches('tmp_before.patch',
                                 'tmp_after.patch',
                                 banner1, banner2)


if __name__ == '__main__':
  Main(sys.argv[1:])
