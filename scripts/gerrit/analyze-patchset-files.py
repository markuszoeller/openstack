import json
import requests

GERRIT_URL = "https://review.openstack.org/"
REVIEW_CHANGE_DETAILS_FILE = 'all_the_reviews.json'


def write_changes_overview_json():
    reviews_all = []
    change_ids = set()
    has_more_reviews = True
    start = 0
    # 500 = max internal paging size of gerrit
    size = 500
    while has_more_reviews:
        has_more_reviews = False
        query = "project:openstack/nova" \
                "+NOT+age:6months" \
                "+branch:master" \
                "&o=ALL_REVISIONS&o=ALL_FILES" \
                "&n=%s" \
                "&S=%s" % (size, start)

        review_url = GERRIT_URL + "/changes/?q=%s" % query
        response = requests.get(review_url)
        invalid_json = response.text
        valid_json = '\n'.join(invalid_json.split('\n')[1:])
        reviews = json.loads(valid_json)
        reviews_all.extend(reviews)
        for r in reviews:
            change_ids.add(r["change_id"])
            if '_more_changes' in r and r['_more_changes']:
                has_more_reviews = True
                start += size

    with open(REVIEW_CHANGE_DETAILS_FILE, 'w') as f:
        f.write(json.dumps(reviews_all, indent=4, separators=(',', ': ')))

    print("len change ids: " + str(len(change_ids)))


def read_changes_json():
    with open('%s' % REVIEW_CHANGE_DETAILS_FILE) as data_file:
        data = json.load(data_file)
    return data


def read_change_ids():
    data = read_changes_json()
    change_ids = [c['change_id'] for c in data]
    return change_ids


def read_change_revisions():
    revisions = []
    with open(REVIEW_CHANGE_DETAILS_FILE) as data_file:
        changes = json.load(data_file)
    for c in changes:
        for r in c["revisions"]:
            revisions.append({r: c["revisions"][r]})
    return revisions


def write_list_to_file(items, filename):
    with open(filename, 'w') as data_file:
        for item in items:
            data_file.write("%s\n" % item)


def get_files_changes(revisions):
    file_changes = []
    for r in revisions:
        # The revision dict has only one key-values pair
        # => values(0) is the first and only element
        ps_files = [ps for ps in r.values()[0]["files"]]
        file_changes.append(ps_files)
    return file_changes


def keep_if_any_in_path(file_changes, file_path_keep):
    filtered = []
    removed = []

    print("keep changes if any in path %s ..." % file_path_keep)
    for f in file_changes:
        if any(path.startswith(file_path_keep) for path in f):
            filtered.append(f)
        else:
            # example: [u'requirements.txt', u'setup.cfg']
            removed.append(f)
    print("removed %s changes." % len(removed))
    write_list_to_file(removed, 'not-in-path-%schanges.txt' % file_path_keep.replace('/', '-'))
    return filtered


def remove_all_in_path(file_changes, file_path_to_ignore):
    filtered = []
    removed = []
    print("removing all %s only changes..." % file_path_to_ignore)
    for f in file_changes:
        if all(path.startswith(file_path_to_ignore) for path in f):
            removed.append(f)
        else:
            filtered.append(f)
    print("removed %s %s only changes." % (len(removed), file_path_to_ignore))
    write_list_to_file(removed, '%schanges.txt' % (file_path_to_ignore.replace('/', '-')))
    return filtered


def remove_hypervisor_only_changes(file_changes, hypervisor_name):
    removed = []
    filtered = []
    print("removing all %s only changes..." % hypervisor_name)
    for f in file_changes:
        if all(path.startswith("nova/virt/" + hypervisor_name) or
               path.startswith("nova/tests/") for path in f):
            removed.append(f)
        else:
            filtered.append(f)
    print("removed %s %s only changes." % (len(removed), hypervisor_name))
    write_list_to_file(removed, 'nova-%s-changes.txt' % hypervisor_name)
    return filtered


# ===== action starts here =====>

# write_changes_overview_json() # that triggers a Gerrit query; uncomment for the first run
change_ids = read_change_ids()
print("changes: %s" % len(change_ids))
revisions = read_change_revisions()
print("patchsets: %s" % len(revisions))

file_changes = get_files_changes(revisions)
# write_list_to_file(file_changes, 'file_changes.txt')

# TODO: maybe plot hits on directories with a treemap like this one
# http://gvallver.perso.univ-pau.fr/?p=700

print("Number of patchsets before filtering: %s" % len(file_changes))
file_changes = keep_if_any_in_path(file_changes, "nova/")
file_changes = remove_all_in_path(file_changes, "nova/cloudpipe/")
file_changes = remove_all_in_path(file_changes, "nova/cmd/")
file_changes = remove_all_in_path(file_changes, "nova/conf/")
file_changes = remove_all_in_path(file_changes, "nova/db/")
file_changes = remove_all_in_path(file_changes, "nova/hacking/")
file_changes = remove_all_in_path(file_changes, "nova/locale/")
file_changes = remove_all_in_path(file_changes, "nova/tests/")
file_changes = remove_all_in_path(file_changes, "nova/vnc/")
file_changes = remove_hypervisor_only_changes(file_changes, "libvirt")
file_changes = remove_hypervisor_only_changes(file_changes, "hyperv")
file_changes = remove_hypervisor_only_changes(file_changes, "ironic")
file_changes = remove_hypervisor_only_changes(file_changes, "vmwareapi")
file_changes = remove_hypervisor_only_changes(file_changes, "xenapi")
print("Number of patchsets after filtering: %s" % len(file_changes))

write_list_to_file(file_changes, "we-should-check-these-changes.txt")
