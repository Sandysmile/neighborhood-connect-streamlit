from html import escape
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st
from data_source import SOURCE, load_records, filter_records, website_url, email_url

st.set_page_config(page_title='Neighborhood Connect | Houston', page_icon='🏠', layout='wide')
st.markdown('<style>' + Path(__file__).with_name('style.css').read_text() + '</style>', unsafe_allow_html=True)

@st.cache_data(ttl=900, show_spinner=False)
def directory():
    rows, fallback = load_records()
    return rows, fallback, datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

def reset_filters():
    st.session_state.search = ''
    st.session_state.district = 'All districts'
    st.session_state.status = 'All statuses'

@st.dialog('Neighborhood details', width='large')
def details(row):
    districts = ' · '.join('District ' + d for d in row['districts'])
    st.markdown(f'<div class="detail-hero"><div class="eyebrow">SUPER NEIGHBORHOOD {escape(row["number"])}</div><h2>{escape(row["name"])}</h2><p>{escape(row["status"])} · {escape(districts)}</p></div>', unsafe_allow_html=True)
    sections = [
        ('Meet your community', ' · '.join(filter(None, [row['day'], row['time'], row['frequency'], row['format']])) or 'Meeting schedule not provided.'),
        ('Meeting location', ' · '.join(filter(None, [row['venue'], row['address']]))),
        ('Community contacts', ' · '.join(filter(None, [row['contact'], row['position']])) or 'Community representative not listed.'),
        ('Public email', row['email']),
        ('Neighborhood liaison', row['liaison'] or 'No liaison listed.'),
        ('Council recognized', row['recognized'] or 'Recognition date not provided.'),
    ]
    for title, body in sections:
        if body:
            st.markdown(f'<div class="detail-section"><strong>{escape(title)}</strong><p>{escape(body)}</p></div>', unsafe_allow_html=True)
    email, website = email_url(row['email']), website_url(row['website'])
    columns = st.columns(2)
    if email:
        columns[0].link_button('Email neighborhood ↗', email, use_container_width=True)
    if website:
        label = 'Visit Facebook ↗' if 'facebook.com' in website.lower() or 'fb.com' in website.lower() else 'Visit website ↗'
        columns[1].link_button(label, website, use_container_width=True)
    st.caption('Please confirm meeting details with the neighborhood before attending. Missing information is not available in the source directory.')

with st.spinner('Loading neighborhood directory…'):
    rows, fallback, fetched_at = directory()

brand, about = st.columns([4, 1])
brand.markdown('<div class="brand"><span class="home-tile">⌂</span><div><strong>Neighborhood Connect</strong><small>HOUSTON · SUPER NEIGHBORHOODS</small></div><span class="pilot">PILOT</span></div>', unsafe_allow_html=True)
about.link_button('About the program ↗', 'https://www.houstontx.gov/superneighborhoods/')
active = sum(row['status'] == 'Active' for row in rows)
districts = sorted({d for row in rows for d in row['districts']})
st.markdown(f'<section class="hero"><div class="eyebrow">STRONGER NEIGHBORHOODS. A CONNECTED HOUSTON.</div><h1>Your neighborhood.<br><span>Your community.</span></h1><p>Find your Super Neighborhood, connect with local leaders, and discover how to get involved.</p><div class="stats"><span><b>{len(rows)}</b> neighborhoods</span><span><b>{active}</b> active councils</span><span><b>{len(districts)}</b> council districts</span></div></section>', unsafe_allow_html=True)
if fallback:
    st.warning('The live portal is unavailable. Showing the saved directory snapshot from November 2, 2026; information may have changed.')
st.markdown('<div class="find-heading"><h2>Find your neighborhood</h2><p>A place to start. A community to belong to.</p></div>', unsafe_allow_html=True)
with st.container(border=True):
    search, district, status = st.columns([2, 1, 1])
    query = search.text_input('SEARCH NEIGHBORHOODS', placeholder='Search by neighborhood name or number', key='search')
    chosen_district = district.selectbox('COUNCIL DISTRICT', ['All districts'] + districts, key='district')
    chosen_status = status.selectbox('NEIGHBORHOOD STATUS', ['All statuses'] + sorted({row['status'] for row in rows if row['status']}), key='status')
filtered = filter_records(rows, query, chosen_district, chosen_status)
count, reset = st.columns([4, 1])
count.caption(f'{len(filtered)} of {len(rows)} neighborhoods')
reset.button('Reset filters ↺', on_click=reset_filters, use_container_width=True)
if not filtered:
    st.info('No neighborhoods match these filters. Try another name, number, or district.')
for start in range(0, len(filtered), 2):
    columns = st.columns(2)
    for column, row in zip(columns, filtered[start:start + 2]):
        with column.container(border=True):
            status_class = 'active' if row['status'] == 'Active' else 'inactive'
            district_text = ' · '.join('District ' + d for d in row['districts'])
            st.markdown(f'<div class="card-meta"><span>SUPER NEIGHBORHOOD {escape(row["number"])}</span><span class="badge {status_class}">{escape(row["status"])}</span></div><h3>{escape(row["name"])}</h3><p class="districts">{escape(district_text)}</p>', unsafe_allow_html=True)
            if st.button('Open neighborhood ↗', key='open_' + row['number'], use_container_width=True):
                details(row)
st.divider()
st.caption('City of Houston · Super Neighborhood Directory · Public directory prototype')
st.markdown(f'[View source data]({SOURCE})')
if not fallback:
    st.caption(f'Last fetched {fetched_at}. Public data is cached for up to 15 minutes; SharePoint edits appear only after publication to this source.')
