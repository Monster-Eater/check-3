# Group contacts and status audience

- Creating a group and adding members uses the Android/iOS address book. The
  app matches saved phone numbers against accounts that enabled **Let phone
  contacts find me**. It sends numbers for a one-time match; the address book
  is not saved.
- Both group-create and add-member API endpoints recheck that selected accounts
  match the submitted contact numbers. Group membership does not accept
  arbitrary account IDs.
- Statuses are visible to their owner and mutual friends (both users follow
  each other). This is enforced by both the status list and single-status API.
  The privacy setting defaults to **Friends only**; users can also choose
  **Nobody**. The migration changes older Everyone/Followers settings to
  Friends only.
- Apply the new `home` migration during deployment. The Render build script
  already runs migrations.
